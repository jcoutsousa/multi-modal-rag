# Multi-RAG API

## Description

Multi-RAG API is a web application that allows users to upload PDF documents and query them using a Retrieval-Augmented Generation (RAG) approach. This project combines FastAPI for the backend, and HTML/CSS/JavaScript for the frontend.

## Features

- PDF document upload
- Query processing using RAG
- Simple and intuitive user interface

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.12
- pip (Python package manager)
- Node.js and npm (for frontend development, if applicable)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/multi-rag-api.git
   cd multi-rag-api
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. Install additional dependencies (if needed):
   - For PDF processing: `pip install pdf2image pillow`
   - On Ubuntu/Debian: `sudo apt-get install poppler-utils`
   - On macOS: `brew install poppler`
   - On Windows: Download and install poppler manually, then add its bin directory to your PATH.

## Usage

1. Start the FastAPI server:
   ```
   uvicorn api:app --reload
   ```

2. Open a web browser and navigate to `http://localhost:8000`

3. Use the interface to upload a PDF file and submit queries.

## API Endpoints

- `GET /`: Serves the main HTML page
- `POST /upload_pdf/`: Endpoint for uploading PDF files
- `POST /query/`: Endpoint for submitting queries

## Project Structure

multi-rag-api/
│
├── api.py # FastAPI application
├── static/
│ ├── index.html # Main HTML file
│ ├── styles.css # CSS styles
│ └── script.js # JavaScript for frontend functionality
├── requirements.txt # Python dependencies
└── README.md # Project documentation

# Multi-RAG API

[![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-green)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project implements a FastAPI-based API for handling PDF uploads and queries using a RAG (Retrieval-Augmented Generation) approach.
