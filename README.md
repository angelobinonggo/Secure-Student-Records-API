# Secure Student Records API

A Django REST Framework API that enforces Role-Based Access Control (RBAC) using JWT authentication. Built as part of Module 4 Lab Activity 1.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Setup and Installation](#setup-and-installation)
5. [Configuration](#configuration)
6. [User Roles](#user-roles)
7. [API Endpoints](#api-endpoints)
8. [RBAC Access Matrix](#rbac-access-matrix)
9. [Demo Credentials](#demo-credentials)
10. [Postman Testing Guide](#postman-testing-guide)
11. [Technical Reflection](#technical-reflection)

---

## Project Overview

This API manages student academic records and restricts access based on the authenticated user's assigned role:

- **Admin** users can create, read, update, and delete any record.
- **Faculty** users can read and update any record, but cannot create or delete.
- **Student** users can only view their own record and have no write access.

All endpoints (except registration) require a valid JWT Bearer token. Tokens are issued via the SimpleJWT library and expire after 60 minutes by default.

---

## Technology Stack

| Component          | Library / Tool                        |
|--------------------|---------------------------------------|
| Framework          | Django 5.x                            |
| REST API           | Django REST Framework (DRF)           |
| Authentication     | djangorestframework-simplejwt          |
| Database           | SQLite (default, development only)    |
| Language           | Python 3.x                            |

---

## Project Structure

```
Secure-Student-Records-API/
|-- manage.py
|-- db.sqlite3
|-- secure_records/               # Project configuration package
|   |-- settings.py               # JWT and DRF settings
|   |-- urls.py                   # Root URL routing
|-- students/                     # Main application
|   |-- models.py                 # StudentRecord model
|   |-- serializers.py            # DRF serializers
|   |-- permissions.py            # Custom RBAC permission classes
|   |-- views.py                  # API views and ViewSet
|   |-- urls.py                   # App-level URL routing
|   |-- admin.py                  # Django admin registration
|   |-- management/
|       |-- commands/
|           |-- seed_data.py      # Management command to seed demo data
```

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/angelobinonggo/Secure-Student-Records-API.git
cd Secure-Student-Records-API
```

### 2. Install Dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt django-filter
```

### 3. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Demo Data

This creates the Admin, Faculty, and Student groups, four demo user accounts, and sample student records.

```bash
python manage.py seed_data
```

### 5. (Optional) Create a Django Superuser

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`.

---

## Configuration

Key settings in `secure_records/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
    'students',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

---

## User Roles

Roles are implemented using Django's built-in `Group` model. Three groups are created:

| Group   | Description                                              |
|---------|----------------------------------------------------------|
| Admin   | Full CRUD access over all student records                |
| Faculty | Read and update access over all student records          |
| Student | Read access restricted to their own record only          |

Users are assigned to groups at registration via the `role` field, or through the Django Admin panel at `/admin/`.

---

## API Endpoints

### Base URL: `http://127.0.0.1:8000`

#### Authentication

| Method | Endpoint              | Description                         | Auth Required |
|--------|-----------------------|-------------------------------------|---------------|
| POST   | `/api/token/`         | Obtain a JWT access and refresh token | No          |
| POST   | `/api/token/refresh/` | Get a new access token using refresh token | No     |
| POST   | `/api/token/verify/`  | Verify a token is valid             | No            |

#### User Management

| Method | Endpoint         | Description                                  | Auth Required |
|--------|------------------|----------------------------------------------|---------------|
| POST   | `/api/register/` | Register a new user and assign a role        | No            |
| GET    | `/api/me/`       | Retrieve the authenticated user's profile    | Yes           |

#### Student Records

| Method | Endpoint                              | Description                              | Auth Required |
|--------|---------------------------------------|------------------------------------------|---------------|
| GET    | `/api/student-records/`               | List student records                     | Yes           |
| POST   | `/api/student-records/`               | Create a student record (Admin only)     | Yes           |
| GET    | `/api/student-records/{id}/`          | Retrieve a single record                 | Yes           |
| PUT    | `/api/student-records/{id}/`          | Full update of a record                  | Yes           |
| PATCH  | `/api/student-records/{id}/`          | Partial update of a record               | Yes           |
| DELETE | `/api/student-records/{id}/`          | Delete a record (Admin only)             | Yes           |
| GET    | `/api/student-records/by-user/{uid}/` | Get records by user ID (Admin/Faculty)   | Yes           |

#### Django Admin Panel

| URL      | Description                  |
|----------|------------------------------|
| `/admin/`| Django administration panel  |

---

## RBAC Access Matrix

| Action                | Admin | Faculty | Student         |
|-----------------------|-------|---------|-----------------|
| List all records      | Yes   | Yes     | Own record only |
| Retrieve one record   | Yes   | Yes     | Own record only |
| Create record (POST)  | Yes   | No      | No              |
| Update record (PUT)   | Yes   | Yes     | No              |
| Delete record (DELETE)| Yes   | No      | No              |
| View by user ID       | Yes   | Yes     | No              |

Access control is enforced by three custom permission classes in `students/permissions.py`:

- `IsAdminUser` - requires the Admin group; used for create and destroy actions.
- `IsAdminOrFaculty` - requires Admin or Faculty group; used for update actions.
- `IsOwnerOrAdminOrFaculty` - authenticated users; Students are additionally restricted to their own records via object-level permission.

---

## Demo Credentials

These accounts are created by `python manage.py seed_data`.

| Username       | Password        | Role    |
|----------------|-----------------|---------|
| admin_user     | AdminPass123    | Admin   |
| faculty_user   | FacultyPass123  | Faculty |
| student_alice  | AlicePass123    | Student |
| student_bob    | BobPass123      | Student |

---

## Postman Testing Guide

### Step 1 - Obtain a JWT Token

**POST** `http://127.0.0.1:8000/api/token/`

Set the request body to `raw` / `JSON`:

```json
{
    "username": "admin_user",
    "password": "AdminPass123"
}
```

Copy the `"access"` value from the response.

### Step 2 - Set the Authorization Header

For every protected request:

- Go to the **Authorization** tab
- Select type: **Bearer Token**
- Paste the access token

### Step 3 - Test Cases

#### Test 1: Admin creates a student record

**POST** `http://127.0.0.1:8000/api/student-records/`
Body (JSON):
```json
{
    "owner": 3,
    "full_name": "Alice Santos",
    "course": "BSIT",
    "year_level": 2,
    "gpa": "1.75"
}
```
Expected: `201 Created`

#### Test 2: Admin lists all records

**GET** `http://127.0.0.1:8000/api/student-records/`
Expected: `200 OK` with all records

#### Test 3: Faculty updates a record

Token: faculty_user

**PATCH** `http://127.0.0.1:8000/api/student-records/1/`
Body (JSON):
```json
{
    "gpa": "1.50"
}
```
Expected: `200 OK`

#### Test 4: Faculty attempts to delete a record (should fail)

Token: faculty_user

**DELETE** `http://127.0.0.1:8000/api/student-records/1/`
Expected: `403 Forbidden`

#### Test 5: Student views own record

Token: student_alice

**GET** `http://127.0.0.1:8000/api/student-records/`
Expected: `200 OK` with only Alice's own record(s)

#### Test 6: Student attempts to view another record (should fail)

Token: student_alice

**GET** `http://127.0.0.1:8000/api/student-records/2/`
Expected: `404 Not Found` (filtered out by queryset) or `403 Forbidden`

#### Test 7: Student attempts to create a record (should fail)

Token: student_alice

**POST** `http://127.0.0.1:8000/api/student-records/`
Expected: `403 Forbidden`

#### Test 8: Access without token (should fail)

No Authorization header.

**GET** `http://127.0.0.1:8000/api/student-records/`
Expected: `401 Unauthorized`

---

## Technical Reflection

### What was implemented

This project implements a three-tier RBAC system on top of Django REST Framework's standard ViewSet pattern. Rather than using DRF's built-in `IsAdminUser` (which only checks `is_staff`), custom permission classes were written to check Django group membership. This keeps role management flexible — roles can be changed through the admin panel without any code changes.

JWT was chosen over session authentication because it is stateless and suitable for API clients such as Postman or mobile apps. Tokens are short-lived (60 minutes) and can be refreshed without re-authentication using the refresh token endpoint.

The `get_queryset` override ensures that Students are filtered at the database level rather than relying solely on object-level permissions. This prevents information leakage where a student could guess another record's ID and receive a permission error that confirms the record exists.

### Challenges encountered

The main challenge was correctly layering queryset-level filtering and object-level permission checks so that the two approaches work together without redundancy. The solution was to use queryset filtering for Students (so records belonging to others are simply invisible) while keeping object-level checks as a safety net for Admin and Faculty access.

Another consideration was Windows terminal encoding — the seed management command originally used Unicode emoji characters that caused `UnicodeEncodeError` on Windows terminals using the CP1252 code page. These were replaced with plain ASCII equivalents.

### Security considerations

- Tokens are transmitted in the `Authorization` header only — never in the URL.
- The `SECRET_KEY` should be replaced with a strong, randomly generated key and stored in an environment variable (e.g., using `python-decouple` or `django-environ`) before deploying to production.
- `DEBUG = True` and `ALLOWED_HOSTS = ['*']` are development-only settings and must be changed before production deployment.
- The SQLite database is suitable for development and testing. A production deployment should use PostgreSQL or MySQL.