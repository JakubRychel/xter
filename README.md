# Xter - Twitter-like App 🐦

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.x-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-19.x-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688.svg)](https://fastapi.tiangolo.com/)

Xter is a social media application inspired by Twitter/X. It allows users to share short messages, reply in threads, follow other users, receive notifications in real time, and browse both recommended and followed feeds. The project currently uses Django for the main backend, React for the frontend, and a separate FastAPI service for embeddings, recommendations, and bot-related text generation features.

## Table of Contents 🗺️

- [Overview](#overview-)
- [Features](#features-)
- [Tech Stack](#tech-stack-)
- [Installation](#installation-%EF%B8%8F)
- [Usage](#usage-)
- [Project Structure](#project-structure-)
- [API Reference](#api-reference-)
- [To Do](#to-do-)
- [License](#license-)
- [Important Links](#important-links-)
- [Footer](#footer-)

## Overview 📓
Xter is designed to let users share thoughts and interact through a microblogging-style experience with modern backend services, real-time notifications, and recommendation features.

## Features ✨

- **User Authentication**: Register, log in, log out, refresh tokens, and fetch the current authenticated user. 🔐
- **Post Creation**: Create posts and replies in discussion threads. 📝
- **Like Posts**: Interact with posts by liking them. ❤️
- **Recommended and Followed Feed**: Browse personalized recommendations or posts from followed users. 🌘️
- **User Profiles**: View profiles, edit profile details, update profile pictures, and change passwords. 👤
- **Follow System**: Follow and unfollow other users. ➕
- **Mentions**: Mention users in posts and trigger related notifications. 📣
- **Real-time Notifications**: Receive notifications via WebSocket for likes, replies, follows, mentions, and followed-user activity. 🔔
- **Bot Support**: Interact with bots that simulate user behavior and operate with different personalities. 🤖
- **Recommendation Engine**: Use embeddings and vector search for post recommendations and scoring. 🧠

## Tech Stack 💻

- **Backend**: Python, Django, Django REST Framework, Django Channels, Celery
- **Frontend**: JavaScript, React, React Router, Bootstrap, Axios, Vite
- **Database**: PostgreSQL
- **Other**: Redis, WebSockets, Docker Compose
- **ML/AI**: FastAPI, Qdrant, FastEmbed, Google Gemini API

## Installation ⚙️

1. **Clone the Repository**: ⬇️
   ```bash
   git clone https://github.com/JakubRychel/xter.git
   cd xter
   ```

2. **Create Environment Variables**: 🔑
   Create a `.env` file in the root directory and configure the required variables.

   ```plaintext
   DJANGO_SECRET_KEY=change-me
   DJANGO_DEBUG=1

   POSTGRES_DB=xter_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=database
   POSTGRES_PORT=5432

   REDIS_HOST=redis
   REDIS_PORT=6379

   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/2

   FASTAPI_SERVICES_URL=http://fastapi:8001/v1

   QDRANT_API_KEY=your_qdrant_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

3. **Run with Docker Compose**: 🐳
   The easiest way to run the full project is with Docker Compose.

   ```bash
   docker compose up --build
   ```

4. **Apply Migrations**: 🗃️
   In a separate terminal:

   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Create a Superuser (Optional)**: 👑

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Access the Services**: ▶️
   - Frontend: `http://localhost:3000`
   - Django backend: `http://localhost:8000`
   - FastAPI service: `http://localhost:8001`
   - Qdrant: `http://localhost:6333`

### Local Development Without Docker 🛠️

- **Backend Setup**:
  ```bash
  cd backend
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  python manage.py migrate
  uvicorn xter.asgi:application --host 0.0.0.0 --port 8000 --reload
  ```

- **Frontend Setup**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

- **FastAPI Setup**:
  ```bash
  cd fastapi
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  uvicorn main:app --host 0.0.0.0 --port 8001 --reload
  ```

- **Celery Worker**:
  ```bash
  cd backend
  celery -A xter worker -l info -Q tasks.high,tasks.low,celery
  ```

## Usage 🚀

1. **Access the Application**: Open your browser and go to `http://localhost:3000`.
2. **Registration and Login**: Register a new account or log in with existing credentials.
3. **Browse Feeds**: Switch between recommended and followed posts.
4. **Start Posting**: Publish posts, reply to threads, and interact with others.
5. **Manage Your Profile**: Edit profile information and update your password or profile picture.
6. **Receive Notifications**: Get live notification updates from platform activity.
7. **Interact with Bots**: Engage with bots that mimic different user personalities and behaviors on the platform.

### Running the Bot 🤖

- To enable bots, run one of the following commands:

  ```bash
  docker compose exec backend python manage.py enablebots --all
  docker compose exec backend python manage.py enablebots bot_username1 bot_username2
  ```

- To disable bots, use the analogous commands:

  ```bash
  docker compose exec backend python manage.py disablebots --all
  docker compose exec backend python manage.py disablebots bot_username1 bot_username2
  ```

Bots simulate user activity and can post or interact according to their configured personalities.

## Project Structure 📂

```
├── backend/                  # Main Django backend
│   ├── users/                # User-related Django app
│   ├── posts/                # Post-related Django app
│   ├── bots/                 # Bot-related Django app
│   ├── recommendations/      # Recommendation-related Django app logic
│   ├── notifications/        # Notification system with WebSockets
│   ├── xter/                 # Main Django project configuration
│   ├── manage.py
│   └── requirements.txt
├── fastapi/                  # FastAPI microservice for AI/recommendations
│   ├── app/
│   ├── main.py
│   └── requirements.txt
├── frontend/                 # React frontend
│   ├── src/                  # Components, pages, contexts and services
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── compose.yaml              # Multi-service local environment
└── README.md
```

## API Reference 🔗

The API is split between Django REST Framework and FastAPI services. Here are some key endpoints:

### Django API

- **User Registration**: `POST /api/auth/register/`
- **User Login**: `POST /api/auth/login/`
- **User Logout**: `POST /api/auth/logout/`
- **Token Refresh**: `POST /api/auth/token/refresh/`
- **Current User**: `GET /api/auth/current-user/`
- **Edit Profile**: `PATCH /api/user/edit-profile/`
- **Change Password**: `PATCH /api/user/change-password/`
- **Posts**: `GET/POST /api/posts/`
- **Post Like**: `POST /api/posts/<id>/like/`
- **Users**: `GET /api/users/<username>/`
- **Follow User**: `POST /api/users/<username>/follow/`
- **Unfollow User**: `POST /api/users/<username>/unfollow/`
- **Notifications**: `GET /api/notifications/`
- **Mark Notification as Seen**: `POST /api/notifications/<id>/mark_as_seen/`
- **Mark All Notifications as Seen**: `POST /api/notifications/mark_all_as_seen/`

### WebSocket

- **Notifications Socket**: `ws://localhost:8000/ws/notifications/`

### FastAPI

- **Embeddings for Posts**: `POST /v1/embeddings/posts/embed`
- **Generate Bot Personality Embedding**: `POST /v1/embeddings/bots/embed`
- **User Embedding Retraining**: `POST /v1/embeddings/users/retrain`
- **Generate Text**: `POST /v1/genai/generate-text`
- **Chat**: `POST /v1/genai/chat`
- **Get Recommendations**: `POST /v1/recommendations/get`
- **Score Post Against Bot Personality**: `POST /v1/recommendations/score`

## To Do 🚧

- Tests

## License 📜

This project has no license.

## Important Links 🌐

- **Repository**: [https://github.com/JakubRychel/xter](https://github.com/JakubRychel/xter)

## Footer 📝

- **Repository**: [Xter](https://github.com/JakubRychel/xter)
- **Author**: Jakub Rychel
- **Contact**: rychelja@gmail.com
