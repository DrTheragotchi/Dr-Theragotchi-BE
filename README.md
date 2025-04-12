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

## Flutter Integration

The backend is configured to work seamlessly with Flutter mobile applications:

- Full CORS support is enabled for all origins (temporarily)
- All API responses are returned as clean JSON
- Explicit HTTP methods are allowed (GET, POST, PUT, DELETE, OPTIONS, PATCH)
- Preflight requests are cached for 10 minutes to improve performance

For production, you should restrict the `allow_origins` to only your Flutter app's domains.

## User Flow

The application follows this user flow:

1. User enters their nickname (POST /user with action=create)
2. User selects their emotion (POST /user with action=update_emotion)
3. System assigns a character based on the emotion
4. User can chat with their character (POST /chat)
5. User can update their emotion (POST /user with action=update_emotion)

## API Endpoints

### User Management
- **POST /user**
  - Query Parameters:
    - `action` (string, required): Action to perform (create, update_emotion, get)
    - `nickname` (string, required for create): User's nickname
    - `emotion` (string, required for update_emotion): Selected emotion (happy, sad, angry, anxious, calm, excited)
    - `uuid` (string, required for update_emotion and get): User UUID
  - Responses:
    - For create: `{ "uuid": "uuid", "nickname": "string" }`
    - For update_emotion (first time): `{ "character_type": "string", "current_mood": "string", "level": 1 }`
    - For update_emotion (subsequent): `{ "success": true, "new_mood": "string" }`
    - For get: `[{ "uuid": "uuid", "nickname": "string", "character_type": "string", "current_mood": "string", "level": 1, "created_at": "string" }]`

### Chat
- **POST /chat**
  - Query Parameters:
    - `message` (string, required): User message
    - `user_uuid` (string, required): User UUID
  - Response: `{ "reply": "string" }`

## Database Schema

The application expects the following tables in Supabase:

### users
- uuid (primary key)
- nickname (string)
- character_type (enum: tiger, penguin, hamster, pig, dog)
- current_mood (enum: happy, sad, angry, anxious, calm, excited)
- level (integer)
- created_at (timestamp with time zone)

### chats (to be implemented)
- id (primary key)
- user_uuid (foreign key to users.uuid)
- user_message
- llm_response
- created_at (timestamp with time zone)
