# FastAPI Project

## Overview
A FastAPI web application ready for custom development.

## Recent Changes
- **2025-10-09**: Converted to FastAPI web app
  - Installed FastAPI and Uvicorn
  - Created basic API with root and health endpoints
  - Configured server to run on port 5000

## Project Structure
- `main.py` - FastAPI application with API endpoints

## Available Endpoints
- `GET /` - Root endpoint, returns welcome message
- `GET /health` - Health check endpoint

## How to Run
The FastAPI server runs automatically via the configured workflow on port 5000, or you can run:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000
```
