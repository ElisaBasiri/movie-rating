
# Movie Rating System (Phase 1 + Phase 2 Logging)

FastAPI backend for a movie management and rating system with full CRUD, pagination, filtering, many-to-many genres, aggregated ratings, and proper logging (Phase 2).

## Tech Stack
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Dependency Manager**: Poetry
- **Logging**: Python standard `logging` module (Phase 2)

## Project Structure
```
app/
├── controllers/
├── services/
├── repositories/
├── models/
├── schemas/
├── exceptions/
├── db/
├── logging_config.py          # ← Phase 2
├── main.py
scripts/
├── seeddb.sql
├── tmdb_5000_movies.csv
├── tmdb_5000_credits.csv
```

## Prerequisites
- Python 3.12+
- Poetry
- PostgreSQL (or Docker Compose)

## 1. Start with Docker Compose


```bash

docker compose up -d
```


## 2. Seed the Database

# Copy files into the container
docker cp scripts/seeddb.sql movie-postgres:/tmp/seeddb.sql
docker cp scripts/tmdb_5000_movies.csv movie-postgres:/tmp/tmdb_5000_movies.csv
docker cp scripts/tmdb_5000_credits.csv movie-postgres:/tmp/tmdb_5000_credits.csv

# Run the seeding script
docker exec -it movie-postgres psql -U postgres -d movie_db -f /tmp/seeddb.sql
```


## 3. Run the FastAPI Project (Local)

```bash

poetry install

poetry run alembic revision --autogenerate -m "initial"

poetry run alembic upgrade head


# 3. Run the server
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at: **http://localhost:8000**

Swagger UI: **http://localhost:8000/docs**

## 4. Environment Variables (`.env`)

Create a `.env` file in the root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/movie_db
```

(If you change the Postgres password/port, update it here.)



## API Endpoints (Quick Reference)

| Method | Endpoint                        | Description                     |
|-------|---------------------------------|---------------------------------|
| GET   | `/api/v1/movies`                | List + filter + pagination      |
| GET   | `/api/v1/movies/{movie_id}`     | Movie detail                    |
| POST  | `/api/v1/movies`                | Create movie                    |
| PUT   | `/api/v1/movies/{movie_id}`     | Update movie                    |
| DELETE| `/api/v1/movies/{movie_id}`     | Delete movie                    |
| POST  | `/api/v1/movies/{movie_id}/ratings` | Add rating (1-10)          |


## Phase 2 Logging

- Logging is already configured (`app/logging_config.py`)
- Logs for **GET /api/v1/movies** and **POST /api/v1/movies/{id}/ratings** are active
- You will see INFO / WARNING / ERROR messages in the terminal exactly as required in the Phase 2 document

Example log output:
```
2025-12-10 20:15:33 - app.controllers.movie_controller - INFO - POST /ratings request → movie_id=42 score=8 ...
2025-12-10 20:15:33 - app.services.rating_service - WARNING - Invalid rating value attempted ...
```
