# 🌟 Emogotchi Backend API

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
</div>

<div align="center">
  <p><i>The backend server powering the Emogotchi virtual pet application - where AI meets emotional wellbeing!</i></p>
</div>

## 📋 Overview

Emogotchi is a virtual pet application that helps users track and manage their emotional wellbeing through interaction with an AI companion. The backend provides all the APIs needed to:

- 🧠 Track user emotions and provide tailored responses
- 🐱 Assign virtual pet characters based on user interaction
- 💬 Enable natural language conversations with AI companions
- 📔 Generate diary entries to help users reflect on their emotional journey
- 🔔 Manage notification preferences
- 🍽️ Feed pets to increase user points

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Supabase account with database set up
- Environment variables properly configured

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
# Edit .env with your Supabase credentials and other settings
```

5. Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`

## 🔄 User Flow

<div align="center">
  <img width="700" src="https://via.placeholder.com/700x400.png?text=Emogotchi+User+Flow" alt="User Flow Diagram"/>
</div>

1. 👤 User onboarding with nickname registration
2. 😊 Initial emotion selection
3. 🐶 Virtual pet assignment based on user's emotional state
4. 💬 Regular conversations with the AI companion
5. 📝 Automatic diary generation from conversations
6. 🔄 Emotion updates and pet evolution
7. 🍽️ Feed pet to gain points and evolve the pet

## 📚 API Documentation

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
  - Enables conversation with the AI companion
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
  - Retrieves complete user profile
- **DELETE `/user/{uuid}`**
  - Removes user data and associated records

### Feeding System
- **POST `/update/points`**
  - Updates user points when feeding the pet
  - Enables pet growth and evolution

## 🛠️ Database Schema

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

## 🔐 Security & Performance

- UUID-based authentication for all API endpoints
- Case-insensitive UUID handling for better user experience
- Rate limiting for API endpoints
- CORS configured for secure cross-origin requests
- Async processing for AI-intensive operations

## 🧰 Technologies

- **FastAPI**: High-performance API framework
- **Supabase**: Database and authentication
- **OpenAI**: AI-powered chat and diary generation
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
<div align="center">
  <p>Built with ❤️ by the Emogotchi Team</p>
</div>
