from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import Optional, List
import certifi
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# MongoDB connection string from environment variables
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
DB_NAME = os.getenv("MONGO_DB_NAME", "search")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "person")
SEARCH_INDEX_NAME = os.getenv("MONGO_SEARCH_INDEX_NAME", "personNamePhone")
AUTOCOMPLETE_INDEX_NAME = os.getenv("MONGO_AUTOCOMPLETE_INDEX_NAME", "personNamesAutocomplete")

# Create MongoDB client with SSL certificate verification
client = MongoClient(MONGO_CONNECTION_STRING, tlsCAFile=certifi.where())
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Add this new model class after the imports
class BalanceUpdate(BaseModel):
    email: str
    balance: float

class LoginRequest(BaseModel):
    email: str
    password: str

class TransferRequest(BaseModel):
    from_email: str
    to_email: str
    amount: float

class TransferApproval(BaseModel):
    transfer_id: str
    to_email: str

@app.get("/person")
async def get_person(first_name: str = None, email: str = None):
    try:
        # Build query based on provided parameters
        query = {}
        if first_name:
            query["first_name"] = first_name
        elif email:
            query["email"] = email

        if not query:
            raise HTTPException(status_code=400, detail="Either first_name or email must be provided")
            
        # Perform findOne query
        result = collection.find_one(query)
        
        if result is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Convert ObjectId to string for JSON serialization
        result["_id"] = str(result["_id"])
        return result
        
    except Exception as e:
        logger.error(f"Error in get_person: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/autocomplete/person")
async def autocomplete_person(query: str):
    try:
        # Perform Atlas Search autocomplete aggregation
        pipeline = [
            {
                "$search": {
                    "index": AUTOCOMPLETE_INDEX_NAME,
                    "autocomplete": {
                        "path": "first_name",
                        "query": query
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "first_name": 1,
                    "last_name": 1,
                    "email": 1
                }
            },
            {
                "$sort": {
                    "first_name": 1
                }
            }
        ]
        
        logger.info(f"Autocomplete query: {query}")
        
        # Execute aggregation and convert cursor to list
        results = list(collection.aggregate(pipeline))
        
        if not results:
            raise HTTPException(status_code=404, detail="No matching names found")
            
        return results
        
    except Exception as e:
        logger.error(f"Error in autocomplete_person: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/person/update-balance")
async def update_balance(update: BalanceUpdate):
    try:
        # Validate balance is not negative
        if update.balance < 0:
            raise HTTPException(status_code=400, detail="Balance cannot be negative")

        # Update the person's balance
        result = collection.update_one(
            {"email": update.email},
            {"$set": {"balance": update.balance}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Person not found")

        if result.modified_count == 0:
            return {"message": "Balance unchanged"}

        logger.info(f"Updated balance for {update.email} to {update.balance}")
        return {"message": "Balance updated successfully"}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(login_data: LoginRequest):
    try:
        logger.info(f"Login attempt for email: {login_data.email}")
        
        # Find user by email and password
        query = {
            "email": login_data.email,
            "pwd": login_data.password
        }
        logger.info(f"Searching with query: {query}")
        
        user = collection.find_one(query)
        
        if user is None:
            logger.info(f"No user found for email: {login_data.email}")
            # Let's also check if user exists but password is wrong
            user_exists = collection.find_one({"email": login_data.email})
            if user_exists:
                logger.info("User exists but password doesn't match")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"User found, login successful for email: {login_data.email}")
        # Convert ObjectId to string for JSON serialization
        user["_id"] = str(user["_id"])
        return user
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transfer/create")
async def create_transfer(transfer: TransferRequest):
    try:
        # Validate amount
        if transfer.amount <= 0:
            raise HTTPException(status_code=400, detail="Transfer amount must be positive")

        # Check if sender has sufficient balance
        sender = collection.find_one({"email": transfer.from_email})
        if not sender:
            raise HTTPException(status_code=404, detail="Sender not found")
        
        if sender.get("balance", 0) < transfer.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Check if recipient exists
        recipient = collection.find_one({"email": transfer.to_email})
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")

        # Create transfer object
        transfer_obj = {
            "_id": str(ObjectId()),
            "from_email": transfer.from_email,
            "to_email": transfer.to_email,
            "amount": transfer.amount,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Add transfer to sender's transfers array
        collection.update_one(
            {"email": transfer.from_email},
            {"$push": {"transfers": transfer_obj}}
        )

        # Add transfer to recipient's transfers array
        collection.update_one(
            {"email": transfer.to_email},
            {"$push": {"transfers": transfer_obj}}
        )

        logger.info(f"Created transfer request: {transfer_obj['_id']}")
        return {"message": "Transfer created successfully", "transfer_id": transfer_obj["_id"]}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transfer/approve")
async def approve_transfer(approval: TransferApproval):
    try:
        # Start a session for the transaction
        with client.start_session() as session:
            with session.start_transaction():
                # Find recipient
                recipient = collection.find_one(
                    {"email": approval.to_email},
                    session=session
                )
                if not recipient:
                    raise HTTPException(status_code=404, detail="Recipient not found")

                # Find the transfer in recipient's transfers
                transfer = None
                for t in recipient.get("transfers", []):
                    if t.get("_id") == approval.transfer_id:
                        transfer = t
                        break

                if not transfer:
                    raise HTTPException(status_code=404, detail="Transfer not found")

                if transfer["status"] != "pending":
                    raise HTTPException(status_code=400, detail="Transfer is not pending")

                # Find sender
                sender = collection.find_one(
                    {"email": transfer["from_email"]},
                    session=session
                )
                if not sender:
                    raise HTTPException(status_code=404, detail="Sender not found")

                # Check if sender still has sufficient balance
                if sender.get("balance", 0) < transfer["amount"]:
                    # Update transfer status to failed
                    collection.update_many(
                        {"transfers._id": transfer["_id"]},
                        {
                            "$set": {
                                "transfers.$.status": "failed",
                                "transfers.$.updated_at": datetime.utcnow()
                            }
                        },
                        session=session
                    )
                    raise HTTPException(status_code=400, detail="Insufficient balance")

                # Update sender's balance and transfer status
                result_sender = collection.update_one(
                    {"email": transfer["from_email"]},
                    {
                        "$inc": {"balance": -transfer["amount"]},
                        "$set": {
                            "transfers.$[elem].status": "completed",
                            "transfers.$[elem].updated_at": datetime.utcnow()
                        }
                    },
                    array_filters=[{"elem._id": transfer["_id"]}],
                    session=session
                )

                # Update recipient's balance and transfer status
                result_recipient = collection.update_one(
                    {"email": transfer["to_email"]},
                    {
                        "$inc": {"balance": transfer["amount"]},
                        "$set": {
                            "transfers.$[elem].status": "completed",
                            "transfers.$[elem].updated_at": datetime.utcnow()
                        }
                    },
                    array_filters=[{"elem._id": transfer["_id"]}],
                    session=session
                )

                if not result_sender.modified_count or not result_recipient.modified_count:
                    # If either update fails, the transaction will be rolled back
                    raise HTTPException(status_code=500, detail="Failed to update balances")

                logger.info(f"Approved transfer: {transfer['_id']}")
                # Transaction will be automatically committed if we reach this point
                return {"message": "Transfer approved and completed successfully"}

    except Exception as e:
        logger.error(f"Error approving transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transfers/{email}")
async def get_transfers(email: str):
    try:
        user = collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        transfers = user.get("transfers", [])
        return transfers

    except Exception as e:
        logger.error(f"Error getting transfers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    client.close() 