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

1. User enters their nickname (POST /onboarding)
2. User selects their emotion (POST /character)
3. System assigns a character based on the emotion
4. User can chat with their character (POST /chat)
5. User can update their emotion (PATCH /emotion)
6. User can update their notification status (POST /user with action=update_notification)

## API Endpoints

### Onboarding
- **POST /onboarding**
  - Query Parameters:
    - `nickname` (string, required): User's nickname
  - Response: `{ "uuid": "uuid", "nickname": "string" }`

### Character Selection
- **POST /character**
  - Query Parameters:
    - `emotion` (string, required): Selected emotion (happy, sad, angry, anxious, calm, excited)
    - `user_uuid` (string, required): User UUID
  - Response: `{ "character_type": "string", "current_mood": "string", "level": 1 }`

### Chat
- **POST /chat**
  - Query Parameters:
    - `message` (string, required): User message
    - `user_uuid` (string, required): User UUID
  - Response: `{ "reply": "string" }`

### Emotion
- **PATCH /emotion**
  - Query Parameters:
    - `emotion` (string, required): New emotion (happy, sad, angry, anxious, calm, excited)
    - `user_uuid` (string, required): User UUID
  - Response: `{ "success": true, "new_mood": "string" }`

### User
- **GET /user/{uuid}**
  - Path Parameters:
    - `uuid` (string, required): User UUID
  - Response: `{ "uuid": "uuid", "nickname": "string", "character_type": "string", "current_mood": "string", "level": 1, "isNotified": false, "created_at": "string" }`

- **DELETE /user/{uuid}**
  - Path Parameters:
    - `uuid` (string, required): User UUID
  - Response: `{ "message": "User deleted successfully" }`

### User Operations (Consolidated)
- **POST /user**
  - Query Parameters:
    - `action` (string, required): Action to perform (create, update_emotion, get, update_notification)
    - `nickname` (string, required for create): User's nickname
    - `emotion` (string, required for update_emotion): Selected emotion
    - `uuid` (string, required for update_emotion, get, update_notification): User UUID
    - `isNotified` (boolean, required for update_notification): Notification status
  - Responses:
    - For create: `{ "uuid": "uuid", "nickname": "string" }`
    - For update_emotion (first time): `{ "character_type": "string", "current_mood": "string", "level": 1 }`
    - For update_emotion (subsequent): `{ "success": true, "new_mood": "string" }`
    - For get: `[{ "uuid": "uuid", "nickname": "string", "character_type": "string", "current_mood": "string", "level": 1, "isNotified": false, "created_at": "string" }]`
    - For update_notification: `{ "success": true, "isNotified": true }`

## Database Schema

The application expects the following tables in Supabase:

### users
- uuid (primary key)
- nickname (string)
- character_type (enum: tiger, penguin, hamster, pig, dog)
- current_mood (enum: happy, sad, angry, anxious, calm, excited)
- level (integer)
- isNotified (boolean)
- created_at (timestamp with time zone)

### chats (to be implemented)
- id (primary key)
- user_uuid (foreign key to users.uuid)
- user_message
- llm_response
- created_at (timestamp with time zone)
