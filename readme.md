# Xter - Twitter-like App

## Overview
Xter is a social media application inspired by Twitter, designed to allow users to share short messages, and engage with content in real-time. This project aims to replicate core functionalities of a microblogging platform with a simple and intuitive interface.

## Features
- **User Accounts**: Register and log in to create a personalized profile.
- **Posts**: Share short messages (tweets) with a character limit.
- **Likes and Comments**: Interact with posts through likes and comments.
- **Real-time Updates**: Stay updated with live feeds and notifications.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/JakubRychel/xter.git
   ```
2. **Navigate to the Project Directory**:
   ```bash
   cd xter
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Up the Database**:
   Ensure SQLite is installed. The database file (e.g., `xter.db`) will be created automatically on first run.
   Run migrations to set up the database schema:
   ```bash
   python manage.py migrate
   ```
5. **Set Up Environment Variables**:
   Create a `.venv` file in the root directory and configure necessary variables.
   ```plaintext
   DB_NAME=xter.db
   SECRET_KEY=your_secret_key
   ```
6. **Run the Application**:
   ```bash
   python manage.py runserver
   ```

## Usage
- Access the application via `http://localhost:8000` (or the port specified in your setup).
- Register a new account or log in with existing credentials.
- Start posting
