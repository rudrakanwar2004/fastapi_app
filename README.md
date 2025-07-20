# Student Eligibility Checker API

This FastAPI application validates student eligibility for various college courses based on 12th-grade marks, qualification exams, and predefined cut-offs. It also logs all requests and responses with timestamps.

---

## Table of Contents

1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [API Documentation & Testing](#api-documentation--testing)
9. [Logging](#logging)
10. [Sample Requests](#sample-requests)

---

## Features

* Validate user input using Pydantic and regex:

  * Name (letters & spaces)
  * Age (17–25)
  * Gender (Male, Female, Other)
  * Marks (0–100 per subject)
  * Desired course (predefined list)
* Check eligibility per course rules (mandatory subjects + exam + cut-off).
* Recommend alternative courses if ineligible.
* Unique student IDs (UUID4).
* Separate `input.log` & `output.log` with timestamps.
* Graceful error handling with HTTP 400 responses.

## Technology Stack

* **Python 3.8+**
* **FastAPI** for building the API
* **Pydantic** for input validation
* **SQLite3** (built-in) for lightweight data storage (if extended)
* **Logging** module for request/response logs

## Prerequisites

* Python 3.8 or above installed
* `pip` package manager
* (Optional) [virtualenv](https://pypi.org/project/virtualenv/) or `venv`

## Project Structure

```plaintext
py_app/
├── main.py          # Application entrypoint
├── .gitignore       # Git ignore patterns
├── README.md        # This file
├── input.log        # Auto-generated request logs
├── output.log       # Auto-generated response logs
└── requirements.txt # (Optional) pinned dependencies
```

## Setup & Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/student-eligibility.git
   cd student-eligibility
   ```

2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install fastapi uvicorn pydantic
   ```

   *(Or, if using `requirements.txt`:)*

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

* No additional configuration is required by default.
* To change log file names or paths, update the logger setup in `main.py`.

## Running the Application

Start the FastAPI server using **Uvicorn**:

```bash
uvicorn main:app --reload
```

* Access the API at `http://127.0.0.1:8000/`
* `--reload` enables hot-reloading on code changes.

## API Documentation & Testing

FastAPI provides interactive docs:

* **Swagger UI**: `http://127.0.0.1:8000/docs`

Use these to call the `/check-eligibility` endpoint and explore request/response schemas.

## Logging

* **input.log**: Incoming JSON requests with timestamps.
* **output.log**: API responses with timestamps.

Each log entry follows:

```plaintext
2025-07-20 17:09:53,432 {"name":"Rudra", ...}
2025-07-20 17:09:53,433 {"student_id":"...","eligible":true}
```

## Sample Requests

**1. Eligible for CSE**

```bash
curl -X POST http://127.0.0.1:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rudra Kanwar",
    "age": 19,
    "gender": "Male",
    "marks": {"Physics":85, "Chemistry":80, "Mathematics":90, "English":75},
    "qualification": {"exam":"JEE", "qualified":true},
    "desired_course": "CSE"
  }'
```

**2. Ineligible for MBBS (recommend alternatives)**

```bash
curl -X POST http://127.0.0.1:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rahul Verma",
    "age": 20,
    "gender": "Male",
    "marks": {"Physics":78, "Chemistry":82, "Biology":85, "English":75},
    "qualification": {"exam":"NEET", "qualified":true},
    "desired_course": "MBBS"
  }'
```
