# Dr. Teragotchi Backend

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
</div>

<div align="center">
  <p>Backend server powering the Dr. Teragotchi emotional wellbeing application</p>
</div>

## About the Backend

This repository contains the backend API for Dr. Teragotchi, a virtual pet companion application that helps users track and improve their emotional wellbeing. The backend provides intelligence for emotional analysis, pet evolution, and diary generation through a series of carefully designed API endpoints.

## API Features

- **Chat Processing**: Interprets user messages and generates contextually appropriate, natural-sounding pet responses
- **Emotional Analysis**: Identifies user emotions from conversation patterns to personalize interactions
- **Pet Assignment**: Algorithmically matches users with appropriate pet companions based on emotional patterns
- **Points & Evolution**: Manages pet growth through feeding and interaction metrics
- **Diary Generation**: Creates reflective diary entries from conversations without user effort
- **User Management**: Handles profiles, settings, and persistent user data

## Architecture

- **FastAPI Framework**: High-performance, async-compatible API endpoints
- **Supabase Integration**: Robust database management for user data, chat history, and diary entries
- **OpenAI Implementation**: Carefully engineered prompts for naturalistic conversation flow
- **Stateful Conversation**: Context management across multiple user interactions
- **Asynchronous Processing**: Non-blocking operations for responsive user experience

## Technical Highlights

- **Advanced Prompt Engineering**: Crafted custom prompts that balance personality with therapeutic value
- **Conversation State Management**: Technical implementation to track conversation context
- **Dynamic Response Generation**: Variable response lengths (brief to moderate) for natural conversation flow
- **Efficient API Integration**: Optimized API calls to minimize latency and costs
- **Structured Data Handling**: Robust schema design for user, pet, and interaction data

## Core API Endpoints

- **/onboarding**: User registration and profile creation
- **/character**: Pet personality assignment based on emotional analysis
- **/chat**: Real-time conversation processing with emotional tracking
- **/diary/generate**: Automatic diary creation from conversation history
- **/user/update/points**: Pet feeding and growth system
- **/user/update/level**: Pet evolution management
- **/user/update/name**: User profile management

## Development Challenges

The backend implementation required solving several technical challenges:
- Balancing response length for natural conversation
- Managing OpenAI API rate limits while maintaining responsiveness
- Creating a stateful experience in a stateless architecture
- Implementing efficient context tracking for meaningful pet-user relationships
- Optimizing database operations for real-time interactions

## Hackathon Implementation

The backend was developed in under 24 hours during an intensive hackathon session, requiring efficient architecture decisions and focused API development. The entire system was built with scalability in mind, allowing for future feature expansion beyond the hackathon prototype.

