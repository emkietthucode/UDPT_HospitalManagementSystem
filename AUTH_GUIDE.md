# Authentication System Documentation

## Overview
The Patient Service now includes a comprehensive JWT-based authentication system with role-based access control (RBAC).

## User Roles
- **patient**: Regular patients who can view their own information
- **doctor**: Medical doctors who can view and manage patient records  
- **receptionist**: Hospital staff who can create, update, and manage patient records

## Authentication Endpoints

### 1. Register User
**POST** `/api/v1/auth/register`

Request body:
```json
{
  "email": "user@hospital.com",
  "full_name": "User Name",
  "role": "doctor|patient|receptionist",
  "password": "password123",
  "is_active": true
}
```

Response:
```json
{
  "email": "user@hospital.com",
  "full_name": "User Name", 
  "role": "doctor",
  "is_active": true,
  "id": "user_id",
  "created_at": "2025-08-21T...",
  "updated_at": "2025-08-21T..."
}
```

### 2. Login
**POST** `/api/v1/auth/login`

Request body:
```json
{
  "email": "user@hospital.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 3. Get Current User
**GET** `/api/v1/auth/me`

Headers:
```
Authorization: Bearer <token>
```

Response:
```json
{
  "email": "user@hospital.com",
  "full_name": "User Name",
  "role": "doctor",
  "is_active": true,
  "id": "user_id",
  "created_at": "2025-08-21T...",
  "updated_at": "2025-08-21T..."
}
```

## Protected Patient Endpoints

All patient endpoints now require authentication with appropriate roles:

### Access Permissions:
- **Create Patient**: `receptionist`, `doctor`
- **List Patients**: `receptionist`, `doctor`  
- **View Patient**: `patient`, `doctor`, `receptionist` (all authenticated users)
- **Update Patient**: `receptionist`, `doctor`
- **Delete Patient**: `receptionist` only
- **Patient Count**: `receptionist`, `doctor`
- **Insurance Validation**: `receptionist`, `doctor`

### Using Protected Endpoints
Include the JWT token in the Authorization header:

```bash
curl -X GET "http://localhost:8001/api/v1/patients" \
  -H "Authorization: Bearer <your_jwt_token>"
```

## Testing the System

### 1. Register a Doctor
```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "full_name": "Dr. John Smith",
    "role": "doctor",
    "password": "password123",
    "is_active": true
  }'
```

### 2. Login and Get Token
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com", 
    "password": "password123"
  }'
```

### 3. Use Token to Access Protected Resources
```bash
curl -X GET "http://localhost:8001/api/v1/patients" \
  -H "Authorization: Bearer <token_from_login>"
```

## Security Features

1. **Password Hashing**: Passwords are hashed using bcrypt
2. **JWT Tokens**: Secure token-based authentication with expiration
3. **Role-Based Access Control**: Different permissions based on user roles
4. **MongoDB Integration**: User data stored securely in MongoDB Atlas
5. **Environment Variables**: Sensitive configuration stored in .env files

## Configuration

The system uses the following environment variables in `.env`:

```
# JWT Authentication
SECRET_KEY=your-very-secure-secret-key-change-this-in-production-environment

# MongoDB connection
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/hospital_management
```

## Error Responses

### 401 Unauthorized
```json
{"detail": "Could not validate credentials"}
```

### 403 Forbidden  
```json
{"detail": "Not enough permissions"}
```

### 400 Bad Request
```json
{"detail": "Email already registered"}
```

## Next Steps

1. **Frontend Integration**: Update the frontend to handle authentication flows
2. **Password Reset**: Implement password reset functionality
3. **Session Management**: Add refresh tokens for better security
4. **Audit Logging**: Log all authentication and authorization events
5. **Rate Limiting**: Add rate limiting to prevent brute force attacks
