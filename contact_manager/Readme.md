# Contact Manager API
A complete Contact Management System built with FastAPI, SQLModel, and JWT authentication. This API allows users to manage their personal contacts with full CRUD operations and secure authentication.

Features
User Authentication: JWT-based secure authentication system

Contact Management: Full CRUD operations for contacts

Data Isolation: Users can only access their own contacts

Request Logging: Middleware to log IP addresses of all requests

CORS Enabled: Cross-Origin Resource Sharing support

SQL Database: SQLite database with SQLModel ORM

Input Validation: Comprehensive data validation

API Endpoints
Authentication Endpoints
Method	Endpoint	Description	Authentication
POST	/register	Register a new user	No
POST	/token	Login and get access token	No
Contact Endpoints (Require Authentication)
Method	Endpoint	Description
POST	/contacts/	Create a new contact
GET	/contacts/	Get all user's contacts
GET	/contacts/{id}	Get a specific contact
PUT	/contacts/{id}	Update a contact
DELETE	/contacts/{id}	Delete a contact
Installation & Setup
Clone the repository:

bash
git clone https://github.com/abdullateef-max/fastAPI-3.git
cd contact_manager
Install dependencies:

bash
pip install -r requirements.txt
Run the application:

bash
python -m contact_manager.main
Access the API:
The API will be available at http://localhost:8000

Usage with Postman
1. Register a New User
Request:

Method: POST

URL: http://localhost:8000/register

Body (raw JSON):

json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
Response:

json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
2. Login to Get Access Token
Request:

Method: POST

URL: http://localhost:8000/token

Body (raw JSON):

json
{
  "username": "testuser",
  "password": "password123"
}
Response:

json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
3. Create a Contact (Authenticated)
Request:

Method: POST

URL: http://localhost:8000/contacts/

Headers:

Authorization: Bearer <your_access_token>

Content-Type: application/json

Body (raw JSON):

json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "123-456-7890"
}
4. Get All Contacts (Authenticated)
Request:

Method: GET

URL: http://localhost:8000/contacts/

Headers:

Authorization: Bearer <your_access_token>

5. Update a Contact (Authenticated)
Request:

Method: PUT

URL: http://localhost:8000/contacts/1

Headers:

Authorization: Bearer <your_access_token>

Content-Type: application/json

Body (raw JSON):

json
{
  "phone": "987-654-3210"
}
6. Delete a Contact (Authenticated)
Request:

Method: DELETE

URL: http://localhost:8000/contacts/1

Headers:

Authorization: Bearer <your_access_token>

Data Models
User Model
python
{
  "id": int,
  "username": str,
  "email": str,
  "hashed_password": str,
  "created_at": datetime
}
Contact Model
python
{
  "id": int,
  "name": str,
  "email": str,
  "phone": str,
  "user_id": int,
  "created_at": datetime,
  "updated_at": datetime
}
Error Responses
The API returns appropriate HTTP status codes:

200 OK: Request succeeded

201 Created: Resource created successfully

400 Bad Request: Invalid input data

401 Unauthorized: Authentication required or invalid token

404 Not Found: Resource not found

500 Internal Server Error: Server error

Security Notes
Passwords are hashed using bcrypt before storage

JWT tokens expire after 30 minutes

All authenticated endpoints require a valid JWT token

Users can only access their own contacts

CORS is enabled for cross-origin requests

Development
To modify or extend this API:

The main application logic is in main.py

Database models are defined in models.py

Authentication logic is in auth.py

Database configuration is in database.py

Middleware is in middleware.py

License