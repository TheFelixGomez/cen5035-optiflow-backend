# OptiFlow Backend

Backend API for OptiFlow - A supply chain optimization and inventory management system.

**Course:** CEN5035 Software Engineering  
**Institution:** Florida Atlantic University

## Overview

OptiFlow is a comprehensive supply chain management platform that helps businesses optimize their inventory, manage vendors, track orders, and generate reports. This repository contains the backend API built with FastAPI and MongoDB.

## Features

- **Authentication & Authorization** - JWT-based user authentication
- **User Management** - User profiles and role management
- **Order Management** - Create, track, and manage orders
- **Vendor Management** - Manage supplier relationships
- **Product Catalog** - Product inventory and management
- **Calendar Integration** - Schedule and track events
- **Reporting** - Generate PDF reports and analytics

## Tech Stack

- **Framework:** FastAPI
- **Database:** MongoDB
- **Authentication:** JWT with Argon2 password hashing
- **Python Version:** 3.13+
- **Package Manager:** uv

## Prerequisites

- Python 3.13 or higher
- MongoDB instance
- uv package manager (recommended)

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/TheFelixGomez/cen5035-optiflow-backend
cd cen5035-optiflow-backend

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development Mode

```bash
# Using uv
uv run fastapi dev app/main.py

# Or with a virtual environment activated
fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
# Using uv
uv run fastapi run app/main.py

# Or with a virtual environment activated
fastapi run app/main.py
```

### Using Docker

```bash
# Build the image
docker build -t optiflow-backend .

# Run the container
docker run -p 80:80 --env-file .env optiflow-backend
```

## API Documentation

Once the application is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## API Endpoints

- `GET /ping` - Health check endpoint
- `GET /db-ping` - Database connectivity check
- `/auth/*` - Authentication endpoints
- `/users/*` - User management endpoints
- `/orders/*` - Order management endpoints
- `/vendors/*` - Vendor management endpoints
- `/products/*` - Product management endpoints
- `/calendar/*` - Calendar and scheduling endpoints
- `/reporting/*` - Report generation endpoints

## Project Structure

```
cen5035-optiflow-backend/
├── app/
│   ├── auth/           # Authentication & authorization
│   ├── users/          # User management
│   ├── orders/         # Order management
│   ├── vendors/        # Vendor management
│   ├── products/       # Product catalog
│   ├── calendar/       # Calendar & scheduling
│   ├── reporting/      # Report generation
│   ├── database.py     # Database connection
│   └── main.py         # Application entry point
├── migrations/         # Database migrations
├── Dockerfile         # Docker configuration
├── pyproject.toml     # Project metadata and dependencies
└── README.md          # This file
```

## Development

### Database Migrations

This directory currently holds a script outside the main application to create fake products data for testing purposes.

### Code Style

This project follows standard Python conventions. Using `Ruff` for linting and formatting is recommended.

## License

This project is developed for educational purposes as part of CEN5035 Software Engineering course at Florida Atlantic University.
