# Movie Rating System

A FastAPI-based RESTful API service for managing movies and user ratings. It uses PostgreSQL as the database, SQLAlchemy for ORM, Alembic for migrations, and includes basic logging.

## Features

- List movies with pagination, filtering by title, release year, or genre.
- Retrieve detailed information about a specific movie, including average rating and ratings count.
- Create, update, and delete movies.
- Submit ratings for movies (scores between 1 and 10).
- Logging for key operations (e.g., fetching movie lists, submitting ratings) at INFO, DEBUG, WARNING, and ERROR levels.
- Seeded with sample data from TMDB (top 1000 movies).

## Project Structure
```
.
├── app/
│   ├── controllers/
│   │   └── movie_controller.py
│   ├── db/
│   │   └── session.py
│   ├── exceptions/
│   │   └── custom_exceptions.py
│   ├── logging.py
│   ├── main.py
│   ├── models/
│   │   ├── director.py
│   │   ├── genre.py
│   │   ├── movie.py
│   │   ├── movie_genre.py
│   │   └── rating.py
│   ├── repositories/
│   │   ├── director_repository.py
│   │   ├── genre_repository.py
│   │   ├── movie_repository.py
│   │   └── rating_repository.py
│   ├── schemas/
│   │   ├── director.py
│   │   ├── genre.py
│   │   ├── movie.py
│   │   └── rating.py
│   └── services/
│       ├── movie_service.py
│       └── rating_service.py
├── alembic/
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       └── 2158bad7724c_initial.py
├── scripts/
│   ├── seed_check.py
│   ├── seeddb.sql
│   ├── tmdb_5000_credits.csv
│   └── tmdb_5000_movies.csv
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
└── .env
```

## Prerequisites

- Python 3.11+
- Docker (for PostgreSQL database)
- Poetry (for dependency management)

## Setup Instructions

1. **Install Poetry** (if not already installed):
   ```
   pip install poetry
   ```

2. **Install Dependencies**:
   ```
   poetry install
   ```

3. **Set Up the Database**:
   - Start PostgreSQL using Docker:
     ```
     docker compose up -d
     ```
   - Copy seeding files to the container (replace `[CONTAINER_NAME]` with your container name, e.g., `movie_rating_db`):
     ```
     docker cp scripts/seeddb.sql [CONTAINER_NAME]:/tmp/seeddb.sql
     docker cp scripts/tmdb_5000_movies.csv [CONTAINER_NAME]:/tmp/tmdb_5000_movies.csv
     docker cp scripts/tmdb_5000_credits.csv [CONTAINER_NAME]:/tmp/tmdb_5000_credits.csv
     ```
   - Execute the seeding script:
     ```
     docker exec -it [CONTAINER_NAME] psql -U postgres -d movie_db -f /tmp/seeddb.sql
     ```
   - Verify seeding (optional):
     ```
     poetry run python scripts/seed_check.py
     ```

4. **Run Database Migrations** (Alembic is already initialized):
   ```
   poetry run alembic revision --autogenerate -m "initial"
   
   poetry run alembic upgrade head
   ```

5. **Configure Environment**:
   - Copy `.env.example` to `.env` and update if needed (e.g., `DATABASE_URL=postgresql://postgres:password@localhost:5432/movie_db`).

## Running the Application

- Start the FastAPI server:
  ```
  poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```

Server will start at: **http://localhost:8000**

Swagger UI: **http://localhost:8000/docs**


## API Endpoints

All endpoints are prefixed with `/api/v1/movies`.

- **GET /**: List movies (paginated).
  - Query params: `page` (default: 1), `page_size` (default: 10), `title`, `release_year`, `genre`.
  - Response: Paginated list with movie summaries (id, title, release_year, director, genres, average_rating).

- **GET /{movie_id}**: Get movie details.
  - Response: Detailed movie info including cast, ratings_count, updated_at.

- **POST /**: Create a new movie.
  - Body: JSON with `title` (required), `director_id` (required), `release_year`, `cast`, `genres` (list of IDs).
  - Response: Created movie details (201 Created).

- **PUT /{movie_id}**: Update a movie.
  - Body: JSON with optional fields to update.
  - Response: Updated movie details.

- **DELETE /{movie_id}**: Delete a movie.
  - Response: 204 No Content.

- **POST /{movie_id}/ratings**: Submit a rating.
  - Body: JSON with `score` (1-10).
  - Response: Created rating (201 Created).

## Logging

- Logging is configured in `app/logging.py` at DEBUG level.
- Logs are output to stdout with format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
- Specific logs for movie listing and rating submission, including success, warnings (e.g., invalid rating), and errors (e.g., database failures).
- - You will see INFO / WARNING / ERROR messages in the terminal exactly as required in the Phase 2 document

## Development Notes

- Use `poetry shell` to activate the virtual environment.
- Add dependencies with `poetry add <package>`.
- Run migrations with `poetry run alembic revision --autogenerate -m "description"` and `poetry run alembic upgrade head`.

## License

This project is unlicensed (for demonstration purposes).
