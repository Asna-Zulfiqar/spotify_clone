# 🎵 Spotify Clone Backend

This is a Spotify Clone backend built with Django REST Framework and PostgreSQL, replicating core music streaming functionalities like songs, albums, artists, playlists, search, user subscriptions, and recommendations.
It also integrates Stripe Connect for artist payments.


## 🚀 Features

- User Authentication (Login, Register, Google Login)
- Artist & Listener Profiles
- Songs, Albums, Artists, Playlists Management
- Full-Text Search across songs, albums, artists, playlists
- Personalized Recommendations for users
- User Subscriptions (Subscribe to Premium Version)
- Like/Dislike Songs

## 🛠 Tech Stack
- Backend: Django, Django REST Framework
- Database: PostgreSQL 
- Payments: Stripe Connect (dj-stripe)


## ⚙️ Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Asna-Zulfiqar/spotify_clone.git
    cd spotify_clone
    ```

2. **Install dependencies with Pipenv:**
    ```bash
    pipenv install
    ```

3. **Activate the virtual environment:**
    ```bash
    pipenv shell
    ```

4. **Set up PostgreSQL database and configure `.env`:**
    - Create a PostgreSQL database.
    - Add your database credentials and environment variables inside a `.env` file.

5. **Run migrations:**
    ```bash
    python manage.py migrate
    ```

6. **Create a superuser (admin):**
    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

### 🔑 Environment Variables (`.env`)

Make sure to create a `.env` file in the root directory and add the following variables:

| Key                     | Description                                 |
|:-------------------------|:-------------------------------------------|
| `DEBUG`                  | Django debug mode (True/False)             |
| `SECRET_KEY`             | Django secret key                         |
| `DATABASE_URL`           | PostgreSQL database URL                   |
| `STRIPE_LIVE_MODE`       | Stripe live mode (True/False)              |
| `STRIPE_TEST_PUBLIC_KEY` | Stripe test public key                    |
| `STRIPE_TEST_SECRET_KEY` | Stripe test secret key                    |
| `PRICE_ID_MONTHLY`       | Stripe price ID for monthly subscription  |
| `PRICE_ID_YEARLY`        | Stripe price ID for yearly subscription   |
| `PRICE_ID_WEEKLY`        | Stripe price ID for weekly subscription   |



