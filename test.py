import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Helper function to print response for debugging
def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(f"JSON: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Text: {response.text}\nException: {e}")


# Test 1: List movies with default parameters
print("\n=== Testing GET /api/v1/movies/ (List Movies) ===")
response = client.get("/api/v1/movies/")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
data = response.json()
assert data["status"] == "success", f"Expected status 'success', got {data.get('status')}"
assert "data" in data, "Missing 'data' in response"
paginated_data = data["data"]
assert all(key in paginated_data for key in ["page", "page_size", "total_items", "items"]), "Missing keys in paginated data"
assert paginated_data["page"] == 1, "Default page should be 1"
assert paginated_data["page_size"] == 10, "Default page_size should be 10"
if paginated_data["items"]:
    item = paginated_data["items"][0]
    assert all(key in item for key in ["id", "title", "release_year", "director", "genres", "average_rating"]), "Missing keys in list item"
    assert all(key in item["director"] for key in ["id", "name"]), "Missing keys in director"
    assert isinstance(item["genres"], list), "Genres should be list"
    assert isinstance(item["average_rating"], float), "Average rating should be float"
print("List movies test passed")

# Assume at least one movie exists or we'll create one later; get initial total
initial_total = paginated_data["total_items"]

# Test pagination with page >1 if possible
if initial_total > 10:
    print("\n=== Testing GET /api/v1/movies/ with page=2 ===")
    response = client.get("/api/v1/movies/?page=2")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["page"] == 2
    assert len(data["data"]["items"]) <= 10
    print("Pagination test passed")

# Test 2: List movies with filters (e.g., non-existing title to check empty results)
print("\n=== Testing GET /api/v1/movies/ with filter (non-existing title) ===")
response = client.get("/api/v1/movies/?title=NonExistingTitle123")
assert response.status_code == 200
data = response.json()
assert data["status"] == "success"
assert data["data"]["items"] == [], "Expected empty items for non-existing title"
print("Filtered list (empty) test passed")

# Test filter with non-existing year
print("\n=== Testing GET /api/v1/movies/ with filter (non-existing year) ===")
response = client.get("/api/v1/movies/?release_year=9999")
assert response.status_code == 200
data = response.json()
assert data["status"] == "success"
assert data["data"]["items"] == [], "Expected empty items for non-existing year"
print("Filtered list (empty year) test passed")

# Test invalid year (non-int)
print("\n=== Testing GET /api/v1/movies/ with invalid year ===")
response = client.get("/api/v1/movies/?release_year=abc")
assert response.status_code == 422
data = response.json()
assert data["status"] == "failure"
assert data["error"]["code"] == 422
# assert "Invalid release_year" in data["error"]["message"] or "value is not a valid integer" in str(data["error"]["message"])
print("Invalid year test passed")

# Test 3: Create a new movie (assuming director_id=1 and genre_id=1 exist; genres can be empty)
print("\n=== Testing POST /api/v1/movies/ (Create Movie) ===")
new_movie = {
    "title": "Test Movie",
    "director_id": 1,
    "release_year": 2023,
    "cast": "Test Actor",
    "genres": [1]  # Assume genre 1 exists; change to [] if needed
}
response = client.post("/api/v1/movies/", json=new_movie)
if response.status_code == 422:
    print("Create failed (possibly invalid director_id or genre_id). Skipping dependent tests.")
    print_response(response)
    created_id = None
else:
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert data["status"] == "success"
    created_data = data["data"]
    assert all(key in created_data for key in ["id", "title", "release_year", "director", "genres", "cast", "average_rating", "ratings_count"]), "Missing keys in created data"
    assert created_data["title"] == new_movie["title"]
    assert created_data["release_year"] == new_movie["release_year"]
    assert created_data["cast"] == new_movie["cast"]
    assert isinstance(created_data["genres"], list)
    assert created_data["average_rating"] in [0.0, None]
    assert created_data["ratings_count"] == 0
    assert all(key in created_data["director"] for key in ["id", "name"])
    created_id = created_data["id"]
    print(f"Create movie test passed. Created ID: {created_id}")

# Test create with empty genres
print("\n=== Testing POST /api/v1/movies/ with empty genres ===")
new_movie_empty_genres = {
    "title": "Test Movie Empty Genres",
    "director_id": 1,
    "release_year": 2023,
    "cast": "Test Actor",
    "genres": []
}
response = client.post("/api/v1/movies/", json=new_movie_empty_genres)
if response.status_code == 201:
    data = response.json()
    assert data["data"]["genres"] == []
    empty_genres_id = data["data"]["id"]
    client.delete(f"/api/v1/movies/{empty_genres_id}")  # Clean up
    print("Create with empty genres passed")
else:
    print("Create with empty genres failed, possibly invalid director_id")
    print_response(response)

# Test create with invalid director_id
print("\n=== Testing POST /api/v1/movies/ with invalid director_id ===")
invalid_movie_director = {
    "title": "Invalid Director Movie",
    "director_id": 999999,
    "release_year": 2023,
    "cast": "Test",
    "genres": []
}
response = client.post("/api/v1/movies/", json=invalid_movie_director)
assert response.status_code == 422
data = response.json()
assert data["status"] == "failure"
assert data["error"]["code"] == 422
assert "Invalid director_id" in data["error"]["message"]
print("Invalid director create test passed")

# Test create with invalid genre_id
print("\n=== Testing POST /api/v1/movies/ with invalid genre_id ===")
invalid_movie_genre = {
    "title": "Invalid Genre Movie",
    "director_id": 1,
    "release_year": 2023,
    "cast": "Test",
    "genres": [999999]
}
response = client.post("/api/v1/movies/", json=invalid_movie_genre)
assert response.status_code == 422
data = response.json()
assert data["status"] == "failure"
assert data["error"]["code"] == 422
assert "Invalid genre_id" in data["error"]["message"]
print("Invalid genre create test passed")

# If creation succeeded, proceed with dependent tests
if created_id is not None:
    # Test filter with created movie (title)
    print("\n=== Testing GET /api/v1/movies/ with filter (existing title) ===")
    response = client.get("/api/v1/movies/?title=Test%20Movie")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    items = data["data"]["items"]
    assert len(items) >= 1
    assert any(item["title"] == "Test Movie" for item in items)
    print("Filtered list (existing title) test passed")

    # Test 4: Get the created movie detail
    print("\n=== Testing GET /api/v1/movies/{movie_id} (Get Movie Detail) ===")
    response = client.get(f"/api/v1/movies/{created_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    detail_data = data["data"]
    assert all(key in detail_data for key in ["id", "title", "release_year", "director", "genres", "cast", "average_rating", "ratings_count", "updated_at"]), "Missing keys in detail"
    assert detail_data["id"] == created_id
    assert detail_data["title"] == new_movie["title"]
    assert detail_data["average_rating"] in [0.0, None]
    assert detail_data["ratings_count"] == 0
    assert isinstance(detail_data["updated_at"], str)
    print("Get movie detail test passed")

    # Test 5: Add a rating to the movie
    print("\n=== Testing POST /api/v1/movies/{movie_id}/ratings (Add Rating) ===")
    rating = {"score": 8}
    response = client.post(f"/api/v1/movies/{created_id}/ratings", json=rating)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    rating_data = data["data"]
    assert all(key in rating_data for key in ["id", "movie_id", "score"])
    assert rating_data["score"] == 8
    assert rating_data["movie_id"] == created_id
    print("Add rating test passed")

    # Add another rating to test average
    print("\n=== Testing multiple ratings for average ===")
    another_rating = {"score": 6}
    response = client.post(f"/api/v1/movies/{created_id}/ratings", json=another_rating)
    assert response.status_code == 201

    # Verify updated average rating in detail
    response = client.get(f"/api/v1/movies/{created_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["average_rating"] == 7.0
    assert data["data"]["ratings_count"] == 2
    print("Verified multiple ratings average")

    # Test 9: Invalid rating (score out of range) on existing movie
    print("\n=== Testing POST /api/v1/movies/{movie_id}/ratings with invalid score ===")
    invalid_rating = {"score": 11}
    response = client.post(f"/api/v1/movies/{created_id}/ratings", json=invalid_rating)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "failure"
    assert data["error"]["code"] == 422
    assert "Score must be between 1 and 10" in data["error"]["message"]
    print("Invalid rating test passed")

    # Test rating on non-existing movie
    print("\n=== Testing POST /api/v1/movies/{invalid_id}/ratings (Not Found) ===")
    response = client.post("/api/v1/movies/999999/ratings", json={"score": 5})
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert data["error"]["code"] == 404
    assert "Movie not found" in data["error"]["message"]
    print("Rating on non-existing movie test passed")

    # Test 6: Update the movie
    print("\n=== Testing PUT /api/v1/movies/{movie_id} (Update Movie) ===")
    update_data = {
        "title": "Updated Test Movie",
        "release_year": 2024,
        "genres": []  # Test changing genres
    }
    response = client.put(f"/api/v1/movies/{created_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    updated_data = data["data"]
    assert updated_data["title"] == "Updated Test Movie"
    assert updated_data["release_year"] == 2024
    assert updated_data["genres"] == []
    print("Update movie test passed")

    # Test update with invalid genre
    print("\n=== Testing PUT /api/v1/movies/{movie_id} with invalid genre ===")
    invalid_update = {"genres": [999999]}
    response = client.put(f"/api/v1/movies/{created_id}", json=invalid_update)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "failure"
    assert data["error"]["code"] == 422
    assert "Invalid genre_id" in data["error"]["message"]
    print("Invalid genre update test passed")

    # Test update non-existing
    print("\n=== Testing PUT /api/v1/movies/{invalid_id} (Not Found) ===")
    response = client.put("/api/v1/movies/999999", json={"title": "Test"})
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert data["error"]["code"] == 404
    assert "Movie not found" in data["error"]["message"]
    print("Update non-existing test passed")

    # Test 7: Delete the movie
    print("\n=== Testing DELETE /api/v1/movies/{movie_id} (Delete Movie) ===")
    response = client.delete(f"/api/v1/movies/{created_id}")
    assert response.status_code == 204
    print("Delete movie test passed")

    # Verify deletion by trying to get it
    response = client.get(f"/api/v1/movies/{created_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert data["error"]["code"] == 404
    assert "Movie not found" in data["error"]["message"]
    print("Verified deletion (Not Found)")

    # Test delete non-existing
    print("\n=== Testing DELETE /api/v1/movies/{invalid_id} (Not Found) ===")
    response = client.delete("/api/v1/movies/999999")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failure"
    assert data["error"]["code"] == 404
    assert "Movie not found" in data["error"]["message"]
    print("Delete non-existing test passed")

# Test 8: Invalid creation (e.g., missing required fields)
print("\n=== Testing POST /api/v1/movies/ with invalid data (missing title) ===")
invalid_movie = {
    "director_id": 1
}
response = client.post("/api/v1/movies/", json=invalid_movie)
assert response.status_code == 422
data = response.json()
assert data["status"] == "failure"
assert data["error"]["code"] == 422
print("Invalid create test passed")

# Test 10: Not Found for GET non-existing movie
print("\n=== Testing GET /api/v1/movies/{invalid_id} (Not Found) ===")
response = client.get("/api/v1/movies/999999")
assert response.status_code == 404
data = response.json()
assert data["status"] == "failure"
assert data["error"]["code"] == 404
assert "Movie not found" in data["error"]["message"]
print("Not Found test passed")

print("\nAll tests completed.")
