# Xter - Twitter-like App 🐦

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-17.x-blue.svg)](https://reactjs.org/)

Xter is a social media application inspired by Twitter. It allows users to share short messages and engage with content in real-time. This project replicates the core functionalities of a microblogging platform with a simple and intuitive interface, built using Django for the backend and React for the frontend.

## Table of Contents 🗺️

- [Overview](#overview-)
- [Features](#features-)
- [Tech Stack](#tech-stack-)
- [Installation](#installation-)
- [Usage](#usage-)
- [Project Structure](#project-structure-)
- [API Reference](#api-reference-)
- [License](#license-)
- [Important Links](#important-links-)
- [Footer](#footer-)

## Overview 📌
Xter is designed to allow users share their thoughts, ideas and opinions quickly and easily.

## Features ✨

- **User Authentication**: Register, log in, and log out securely. 🔐
- **Post Creation**: Share short messages with character limits. 📝
- **Like and Unlike Posts**: Interact with posts by liking them. ❤️
- **Commenting**: Engage in discussions by adding comments to posts. 💬
- **Real-time Feed**: View posts from followed users and recommended content. 🏘️
- **User Profiles**: View user profiles, follow/unfollow users. 👤
- **Bot Support**: Automated bots generate content and interactions. 🤖
- **Recommendation Engine**: Algorithm suggests relevant posts based on user interactions.

## Tech Stack 💻

- **Backend**: Python, Django, Django REST Framework
- **Frontend**: JavaScript, React, Bootstrap, Axios
- **Database**: PostgreSQL (configured in `xter/settings.py`)
- **Other**: Celery (for asynchronous tasks), Redis (for caching and Celery broker)
- **ML/AI**: Sentence Transformers, Google Gemini API, DeBERTa

## Installation ⚙️

1. **Clone the Repository**: ⬇️
   ```bash
   git clone https://github.com/JakubRychel/xter.git
   cd xter
   ```

2. **Backend Setup**: 🐍
   ```bash
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Apply migrations
   python manage.py migrate

   # Create a superuser (admin account)
   python manage.py createsuperuser
   ```

3. **Frontend Setup**: ⚛️
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Variables**: 🔑
   - Set the `GOOGLE_API_KEY` environment variable for bot functionality. Create `.env` file in the root directory and configure necessary variables.

   ```plaintext
   GOOGLE_API_KEY=your_google_api_key
   ```

5. **Database Configuration**: 🗄️
   - The project is configured to use PostgreSQL. Update the `DATABASES` setting in `xter/settings.py` with your PostgreSQL credentials.

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'xter_db',
           'USER': 'postgres',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5434',
       }
   }
   ```

6. **Run the Application**: ▶️
   - Start the Django backend:
     ```bash
     python manage.py runserver
     ```
   - Start the React frontend (in a separate terminal):
     ```bash
     cd frontend
     npm run dev
     ```

## Usage 🚀

1.  **Access the Application**: Open your browser and go to `http://localhost:8000` for the backend and frontend.
2.  **Registration and Login**: Register a new account or log in with existing credentials.
3.  **Start Posting**: Share your thoughts and engage with other users!

### Running the Bot 🤖

- To start the bot, run the following command:

  ```bash
  python manage.py runbots
  ```
This command creates bot users and schedules them to generate content and interact with posts.

## Project Structure 📂

```
├── users/                  # User-related Django app
├── posts/                  # Post-related Django app
├── bots/                   # Bot-related Django app
├── recommendations/      # Recommendation engine Django app
├── xter/                   # Main Django project
├── manage.py
├── frontend/                 # React frontend
│   ├── src/                  # React components and services
│   ├── public/
│   ├── package.json
│   └── webpack.config.js
└── README.md
```

## API Reference 🔗

The API endpoints are defined using Django REST Framework. Here are some key endpoints:

- **User Registration**: `POST /api/auth/register/`
- **User Login**: `POST /api/auth/login/`
- **User Logout**: `POST /api/auth/logout/`
- **Current User**: `GET /api/auth/current-user/`
- **Posts**: `GET/POST /api/posts/`
- **Posts Like**: `POST /api/posts/<id>/like/`
- **Posts Unlike**: `POST /api/posts/<id>/unlike/`
- **Posts Read**: `POST /api/posts/<id>/read/`
- **Follow User**: `POST /api/users/<username>/follow/`
- **Unfollow User**: `POST /api/users/<username>/unfollow/`

## License 📜

This project has no license.

## Important Links 🌐

- **Repository**: [https://github.com/JakubRychel/xter](https://github.com/JakubRychel/xter)

## Footer 📝

- **Repository**: [Xter](https://github.com/JakubRychel/xter)
- **Author**: Jakub Rychel
- **Contact**: rychelja@gmail.com