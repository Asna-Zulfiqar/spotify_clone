# Spotify Clone

A full-featured music streaming platform built with Django Rest Framework and PostgreSQL.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Development Setup](#development-setup)
- [Frontend Integration](#frontend-integration)
- [Deployment](#deployment)
- [Timeline](#timeline)

## Project Overview

This project aims to build a music streaming platform similar to Spotify with features like user authentication, playlist management, music library, search functionality, and media playback.

## Features

### Core Features
- User authentication and authorization
- Music upload and management
- Playlist creation and management
- Artist profiles
- Album organization
- Search functionality
- Media streaming

### Additional Features
- User followers/following system
- Like/save tracks and playlists
- Recommendations based on listening history
- Recently played tracks
- User activity feed

## Tech Stack

### Backend
- **Django**: Web framework
- **Django Rest Framework**: API development
- **PostgreSQL**: Database
- **Pipenv**: Dependency management
- **AWS S3** (recommended): File storage for media files
- **Redis** (optional): Caching and session management

### Suggested Frontend
- **React.js**: Frontend library
- **Redux**: State management
- **Axios**: API communication
- **Tailwind CSS**: Styling
- **Howler.js**: Audio playback

## Project Structure

```
spotify_clone/
├── Pipfile
├── Pipfile.lock
├── README.md
├── manage.py
├── media/
├── static/
├── spotify_clone/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/
│   ├── __init__.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── tests.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── music/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── playlists/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
└── frontend/ (if integrated)
    ├── package.json
    ├── public/
    └── src/
        ├── components/
        ├── containers/
        ├── redux/
        ├── services/
        ├── styles/
        ├── App.js
        └── index.js
```

## API Endpoints

### Authentication
- `POST /api/auth/register/`: User registration
- `POST /api/auth/login/`: User login
- `POST /api/auth/logout/`: User logout
- `GET /api/auth/user/`: Get current user
- `PUT /api/auth/user/`: Update user profile

### Artists
- `GET /api/artists/`: List all artists
- `GET /api/artists/{id}/`: Get artist details
- `GET /api/artists/{id}/albums/`: Get artist albums
- `GET /api/artists/{id}/tracks/`: Get artist tracks

### Albums
- `GET /api/albums/`: List all albums
- `GET /api/albums/{id}/`: Get album details
- `GET /api/albums/{id}/tracks/`: Get album tracks
- `POST /api/albums/`: Create album (admin/artist only)
- `PUT /api/albums/{id}/`: Update album (admin/artist only)
- `DELETE /api/albums/{id}/`: Delete album (admin/artist only)

### Tracks
- `GET /api/tracks/`: List all tracks
- `GET /api/tracks/{id}/`: Get track details
- `POST /api/tracks/`: Upload track (admin/artist only)
- `PUT /api/tracks/{id}/`: Update track (admin/artist only)
- `DELETE /api/tracks/{id}/`: Delete track (admin/artist only)
- `GET /api/tracks/popular/`: Get popular tracks
- `GET /api/tracks/recent/`: Get recently added tracks

### Playlists
- `GET /api/playlists/`: List user playlists
- `GET /api/playlists/{id}/`: Get playlist details
- `POST /api/playlists/`: Create playlist
- `PUT /api/playlists/{id}/`: Update playlist
- `DELETE /api/playlists/{id}/`: Delete playlist
- `POST /api/playlists/{id}/tracks/`: Add track to playlist
- `DELETE /api/playlists/{id}/tracks/{track_id}/`: Remove track from playlist

### Search
- `GET /api/search/?q={query}`: Search tracks, albums, artists, playlists

### User Library
- `GET /api/me/tracks/`: Get saved tracks
- `POST /api/me/tracks/`: Save track
- `DELETE /api/me/tracks/{id}/`: Remove saved track
- `GET /api/me/albums/`: Get saved albums
- `POST /api/me/albums/`: Save album
- `DELETE /api/me/albums/{id}/`: Remove saved album
- `GET /api/me/recently-played/`: Get recently played tracks

## Database Schema

### User
- id (PK)
- username
- email
- password
- profile_picture
- bio
- date_joined

### Artist
- id (PK)
- name
- bio
- profile_picture
- cover_image
- user (FK to User, nullable)

### Album
- id (PK)
- title
- release_date
- cover_image
- artist (FK to Artist)
- genre
- description

### Track
- id (PK)
- title
- artist (FK to Artist)
- album (FK to Album, nullable)
- audio_file
- duration
- genre
- release_date
- plays_count
- featuring (M2M to Artist)

### Playlist
- id (PK)
- title
- description
- cover_image
- user (FK to User)
- is_public
- created_at
- updated_at
- tracks (M2M to Track through PlaylistTrack)

### PlaylistTrack
- id (PK)
- playlist (FK to Playlist)
- track (FK to Track)
- added_at
- position

### UserTrack (for saved/liked tracks)
- id (PK)
- user (FK to User)
- track (FK to Track)
- saved_at

### UserAlbum (for saved/liked albums)
- id (PK)
- user (FK to User)
- album (FK to Album)
- saved_at

### PlayHistory
- id (PK)
- user (FK to User)
- track (FK to Track)
- played_at

## Development Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- pipenv

### Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/spotify-clone.git
   cd spotify-clone
   ```

2. Install dependencies using pipenv:
   ```bash
   pipenv install
   ```

3. Create a `.env` file for environment variables:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgres://user:password@localhost:5432/spotify_clone
   AWS_ACCESS_KEY_ID=your_aws_key (if using S3)
   AWS_SECRET_ACCESS_KEY=your_aws_secret (if using S3)
   AWS_STORAGE_BUCKET_NAME=your_bucket_name (if using S3)
   ```

4. Setup PostgreSQL database:
   ```bash
   createdb spotify_clone
   ```

5. Run migrations:
   ```bash
   pipenv run python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   pipenv run python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   pipenv run python manage.py runserver
   ```

## Frontend Integration

### Option 1: Django Templates with HTMX
For a simpler approach, use Django templates with HTMX for dynamic interactions.

### Option 2: React.js Frontend (Recommended)
For a more modern, responsive UI similar to Spotify:

1. Create a React frontend using Create React App or Next.js
2. Use Redux for state management
3. Implement components for:
   - Player interface
   - Playlist management
   - User profiles
   - Search functionality
   - Music library
4. Connect to the DRF backend using Axios or Fetch API
5. Use JWT authentication for secure API requests

### Implementing the Frontend
```bash
# Create React App
npx create-react-app frontend
cd frontend

# Install dependencies
npm install axios redux react-redux redux-thunk react-router-dom styled-components howler
```

## Deployment

### Backend Deployment (Suggested)
- **Docker** containerization
- **AWS ECS** or **Heroku** for hosting
- **AWS RDS** for PostgreSQL database
- **AWS S3** for media storage
- **CloudFront** for CDN

### Frontend Deployment (Suggested)
- **Vercel** or **Netlify** for React frontend
- **AWS S3** with **CloudFront** as alternative

## Timeline

1. **Week 1-2**: Project setup and authentication
   - Setup development environment
   - Implement user authentication
   - Build basic models

2. **Week 3-4**: Core models and APIs
   - Implement music models (tracks, albums, artists)
   - Create playlist functionality
   - Develop core API endpoints

3. **Week 5-6**: Advanced features
   - Implement search functionality
   - Add user library management
   - Build recommendation system

4. **Week 7-8**: Frontend integration
   - Develop React components
   - Implement player interface
   - Connect to backend APIs

5. **Week 9-10**: Testing and refinement
   - Unit and integration tests
   - Performance optimization
   - UI/UX improvements

6. **Week 11-12**: Deployment and documentation
   - Setup production environment
   - Create documentation
   - Final testing and launch