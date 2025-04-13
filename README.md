# Emogotchi Backend API

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter"/>
</div>

<div align="center">
  <p>Backend service for the Emogotchi virtual pet application</p>
</div>

## Overview

Emogotchi is a virtual pet application that helps users track and manage their emotional wellbeing through interaction with an AI companion. The backend provides APIs for:

- Tracking user emotions with personalized responses
- Assigning virtual pet characters based on user interaction
- Facilitating natural language conversations with AI companions
- Generating diary entries from conversations
- Managing notification preferences
- Pet feeding system with points-based progression

## Getting Started

### Prerequisites

- Python 3.9+
- Supabase account with database set up
- Environment variables configured

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/emogotchi-backend.git
cd emogotchi-backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Configure Supabase credentials and settings in .env
```

5. Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`

## User Flow

1. User registration with nickname
2. Emotion selection
3. Virtual pet assignment
4. Conversations with AI companion
5. Diary generation from conversations
6. Emotion and pet evolution
7. Pet feeding to gain points and advance levels

## API Documentation

### Onboarding
- **POST `/onboarding`**
  - Registers a new user with a nickname
  - Returns UUID for future requests

### Character Management
- **POST `/character`**
  - Assigns a character based on user emotion
  - Returns character type and initial state

### Chat System
- **POST `/chat`**
  - Facilitates conversation with the AI companion
  - Provides therapeutic responses
  - Awards points based on interaction
  - Every 4th message triggers emotional analysis

### Emotion Tracking
- **PATCH `/emotion`**
  - Updates the user's current emotion
  - Affects the pet's appearance and behavior

### Diary System
- **GET `/diary/dates`**
  - Retrieves available diary entry dates
- **GET `/diary/{date}`**
  - Gets detailed diary for specific date
- **POST `/diary/generate`**
  - Creates a new diary entry

### User Management
- **GET `/user/{uuid}`**
  - Retrieves user profile
- **DELETE `/user/{uuid}`**
  - Removes user data and associated records

### Feeding System
- **POST `/user/update/points`**
  - Updates user points when feeding the pet
  - Enables pet growth and evolution
  - Request format: JSON body `{"uuid": "user-uuid", "points": 150}`
  - Response: Empty JSON object with status 200

## Database Schema

### User Table
| Column | Type | Description |
|--------|------|-------------|
| uuid | UUID | Primary key |
| nickname | String | User's display name |
| animal_type | Enum | Pet character type |
| animal_emotion | Enum | Current pet emotion |
| animal_level | Integer | Pet's growth level |
| points | Integer | User's accumulated points |
| is_notified | Boolean | Notification preferences |
| created_at | Timestamp | Account creation time |

### Chat Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| uuid | UUID | User reference |
| user_message | Text | Message from user |
| ai_response | Text | Response from AI |
| created_at | Timestamp | Message timestamp |

### Diary Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| uuid | UUID | User reference |
| date | Date | Entry date |
| summary | Text | AI-generated summary |
| emotion | String | Detected emotion |
| created_at | Timestamp | Entry creation time |

## Flutter Integration

### Setting Up the Flutter Application

1. Clone the Flutter repository:
```bash
git clone https://github.com/your-username/emogotchi-frontend.git
cd emogotchi-frontend
```

2. Install dependencies:
```bash
flutter pub get
```

3. Configure backend URL:
```dart
// lib/config/api_config.dart
// Android Emulator
final String baseUrl = 'http://10.0.2.2:8000';
// iOS Simulator
// final String baseUrl = 'http://localhost:8000';
// Production
// final String baseUrl = 'https://your-production-server.com';
```

4. Run the application:
```bash
flutter run
```

### API Integration Examples

#### User Registration
```dart
Future<String> registerUser(String nickname) async {
  final url = Uri.parse('$baseUrl/onboarding');
  final uuid = Uuid().v4();
  
  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'uuid': uuid, 'nickname': nickname}),
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['uuid'];
  } else {
    throw Exception('Failed to register user');
  }
}
```

#### Pet Feeding
```dart
Future<void> updateUserPoints(String uuid, int points) async {
  final url = Uri.parse('$baseUrl/user/update/points');

  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'uuid': uuid, 'points': points}),
    );

    if (response.statusCode == 200) {
      print("Points updated successfully");
    } else {
      throw Exception(
        'Failed to update user points (status ${response.statusCode}): ${response.body}',
      );
    }
  } catch (e) {
    throw Exception('Error updating user points: $e');
  }
}
```

## Security & Performance

- UUID-based authentication for all endpoints
- Case-insensitive UUID handling
- Rate limiting for API protection
- CORS configured for secure cross-origin requests
- Asynchronous processing for AI operations

## Technologies

- **FastAPI**: API framework
- **Supabase**: Database and authentication
- **OpenAI**: AI-powered conversation and diary generation
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **Flutter**: Cross-platform frontend framework

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
<div align="center">
  <p>Built by Yutaka Yamaguchi, Wonjae Kim, Dexter Jae, Jaegyoon Lee</p>
</div>
