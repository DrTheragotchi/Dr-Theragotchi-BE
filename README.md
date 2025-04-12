# Emogotchi Backend

FastAPI backend for the Emogotchi application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Supabase credentials:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation is available at `http://localhost:8000/docs`

## API Endpoints

- `POST /onboarding`: Create a new user with character type
- `POST /chat`: Send a message and get LLM response
- `GET /user/{uuid}`: Get user information
- `DELETE /user/{uuid}`: Delete a user

## Database Schema

The application expects the following tables in Supabase:

### users
- uuid (primary key)
- character_type
- created_at (timestamp with time zone)

### chats (to be implemented)
- id (primary key)
- user_uuid (foreign key to users.uuid)
- user_message
- llm_response
- created_at (timestamp with time zone)
