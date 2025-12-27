# Chatbot Service

This service provides an AI-powered chatbot for the e-commerce platform. It handles user queries, provides product information, and assists with order tracking.

## 🛠 Tech Stack

- **Language:** Python 3.9+
- **Framework:** FastAPI
- **AI/LLM:** OpenAI API
- **Database:** PostgreSQL (AsyncPG), Redis (Caching)
- **ORM:** SQLAlchemy

## 📂 Project Structure

- `app/`: Main application code.
    - `agents/`: Logic for AI agents.
    - `models/`: Pydantic and SQLAlchemy models.
    - `services/`: Business logic services.
    - `tools/`: Tools used by the agents.
- `database/`: SQL scripts and database initialization.
- `tests/`: Unit and integration tests.

## 🚀 Setup & Run

### 1. Environment Setup

Create a `.env` file in the `chatbot-service` directory (copy from example if available) and configure the following:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/medusa_db
OPENAI_API_KEY=your_openai_api_key
REDIS_URL=redis://localhost:6379
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Service

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

## 🧪 Testing

Run the tests using pytest:

```bash
pytest
```
