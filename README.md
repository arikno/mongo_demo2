# Full-Stack Money Transfer Application

A full-stack application built with FastAPI backend and JavaScript frontend that enables user authentication, person search, and secure money transfers between users.

## Features

- User Authentication (Login/Logout)
- Real-time Person Search with Autocomplete
- Money Transfer System
  - Send money to other users
  - Approve incoming transfers
  - View transfer history
  - Real-time balance updates
- MongoDB Transaction Support
- Modern UI with Bootstrap

## Prerequisites

- Python 3.x
- MongoDB Atlas account
- Modern web browser
- pip (Python package installer)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/arikno/mongo_demo2.git
cd mongo_demo2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following content:
```env
MONGO_CONNECTION_STRING="your_mongodb_connection_string"
MONGO_DB_NAME="search"
MONGO_COLLECTION_NAME="person"
MONGO_SEARCH_INDEX_NAME="personNamePhone"
MONGO_AUTOCOMPLETE_INDEX_NAME="personNamesAutocomplete"
```

## Running the Application

1. Start the backend server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://127.0.0.1:8000`

2. Start the frontend server:
```bash
cd frontend
python3 -m http.server 8080
```
The web interface will be available at `http://localhost:8080`

## API Endpoints

### Authentication
- **POST** `/login`: Authenticate user with email and password

### Person Search
- **GET** `/person`: Get person by email
- **GET** `/autocomplete/person`: Real-time name search with autocomplete

### Money Transfers
- **POST** `/transfer/create`: Create a new money transfer
- **POST** `/transfer/approve`: Approve an incoming transfer
- **GET** `/transfers/{email}`: Get transfer history for a user

### Balance Management
- **POST** `/person/update-balance`: Update user's balance

## Frontend Features

### Authentication
- Login form with email/password
- Welcome message showing user's full name
- Automatic session management

### Search Interface
- Real-time search with autocomplete dropdown
- Search by email functionality
- Person details display

### Transfer System
- Send money to other users
- View and approve incoming transfers
- Transfer history with status indicators
- Real-time balance updates

## Security Features

- MongoDB transactions for safe balance updates
- Secure authentication system
- SSL certificate verification for MongoDB connections
- CORS protection
- Environment variable configuration

## Recent Updates

1. UI Improvements:
   - Removed search button for smoother UX
   - Enhanced welcome message with full name
   - Search now works through dropdown selection
   - Changed search to use email instead of first name

2. Transfer System Enhancement:
   - Added MongoDB transactions for balance updates
   - Atomic operations for money transfers
   - Rollback support on failure
   - Improved transfer status tracking

## Dependencies

### Backend
- fastapi: Web framework
- uvicorn: ASGI server
- pymongo: MongoDB driver
- python-dotenv: Environment variable management
- certifi: SSL certificate verification

### Frontend
- Bootstrap: UI framework
- JavaScript (Vanilla)
- HTML5/CSS3

## Development

The application uses FastAPI's automatic reload feature for the backend and a simple Python HTTP server for the frontend. Any changes to the backend code will trigger a server restart automatically when running with the `--reload` flag.

## Error Handling

- Comprehensive error handling for all API endpoints
- Transaction rollback on failure
- User-friendly error messages in UI
- Detailed server-side logging

## Logging

The application includes comprehensive logging:
- API request/response logging
- Authentication attempts
- Transfer operations
- MongoDB transaction status
- Error tracking

## Testing

To test the application:
1. Start both backend and frontend servers
2. Login with test credentials (e.g., email: "wnu@z.gd", password: "pass123")
3. Try searching for other users
4. Attempt money transfers
5. Login as recipient to approve transfers
6. Check transfer history and balance updates 