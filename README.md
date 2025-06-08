# Person Search API

A FastAPI application that provides a search interface for person records stored in MongoDB Atlas.

## Prerequisites

- Python 3.x
- MongoDB Atlas account
- pip (Python package installer)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following content:
```env
MONGO_CONNECTION_STRING="mongodb+srv://admin:admin@pstt.t5w1vbr.mongodb.net/?retryWrites=true&w=majority&appName=PSTT"
MONGO_DB_NAME="search"
MONGO_COLLECTION_NAME="person"
MONGO_SEARCH_INDEX_NAME="personNamePhone"
MONGO_AUTOCOMPLETE_INDEX_NAME="personNamesAutocomplete"
```

## Running the Application

Start the application using uvicorn:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### Get Person by First Name
- **URL**: `/person`
- **Method**: `GET`
- **Query Parameters**: 
  - `first_name` (required): The first name to search for
- **Success Response**:
  - **Code**: 200
  - **Content**: JSON object containing person details
```json
{
    "_id": "string",
    "first_name": "string",
    "last_name": "string",
    "phone": "string",
    ...
}
```
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"detail": "Person not found"}`

### Autocomplete Person Names
- **URL**: `/autocomplete/person`
- **Method**: `GET`
- **Query Parameters**: 
  - `query` (required): The partial name to search for
- **Success Response**:
  - **Code**: 200
  - **Content**: Array of person objects with matching names
```json
[
    {
        "first_name": "string",
        "last_name": "string",
        "email": "string"
    },
    ...
]
```
- **Error Response**:
  - **Code**: 404
  - **Content**: `{"detail": "No matching names found"}`
  - **Code**: 500
  - **Content**: `{"detail": "Error message"}`

### Update Person's Balance
- **URL**: `/person/update-balance`
- **Method**: `POST`
- **Request Body**:
```json
{
    "email": "string",
    "balance": float
}
```
- **Success Response**:
  - **Code**: 200
  - **Content**: `{"message": "Balance updated successfully"}`
  or
  - **Content**: `{"message": "Balance unchanged"}`
- **Error Response**:
  - **Code**: 400
  - **Content**: `{"detail": "Balance cannot be negative"}`
  - **Code**: 404
  - **Content**: `{"detail": "Person not found"}`
  - **Code**: 500
  - **Content**: `{"detail": "Error message"}`

### Example Usage

Using curl:
```bash
curl "http://127.0.0.1:8000/person?first_name=MARK"
curl "http://127.0.0.1:8000/autocomplete/person?query=MA"
curl -X POST "http://127.0.0.1:8000/person/update-balance" \
  -H "Content-Type: application/json" \
  -d '{"email": "mark.smith@example.com", "balance": 1000.50}'
```

Using Python requests:
```python
import requests

# Search for exact match
response = requests.get("http://127.0.0.1:8000/person", params={"first_name": "MARK"})
print(response.json())

# Autocomplete search
response = requests.get("http://127.0.0.1:8000/autocomplete/person", params={"query": "MA"})
print(response.json())

# Update balance
response = requests.post(
    "http://127.0.0.1:8000/person/update-balance",
    json={
        "email": "mark.smith@example.com",
        "balance": 1000.50
    }
)
print(response.json())
```

## Error Handling

The API includes comprehensive error handling:
- 404: When no person is found with the given first name
- 500: For server-side errors (e.g., database connection issues)

## Development

The application uses FastAPI's automatic reload feature. Any changes to the code will trigger a server restart automatically when running with the `--reload` flag.

## Dependencies

- fastapi: Web framework
- uvicorn: ASGI server
- pymongo: MongoDB driver
- python-dotenv: Environment variable management
- certifi: SSL certificate verification

## Security

- The application uses SSL certificate verification for MongoDB connections
- CORS is enabled for all origins (can be restricted in production)
- Environment variables are used for sensitive configuration

## Logging

The application includes basic logging configuration:
- Logs MongoDB connection issues
- Logs API errors
- Uses Python's built-in logging module 