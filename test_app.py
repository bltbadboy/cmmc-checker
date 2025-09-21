import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_hello_valid_name():
    """Test the /hello/{name} endpoint with a valid name."""
    response = client.get("/hello/Mike")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Mike!"}

def test_hello_valid_name_with_spaces():
    """Test the /hello/{name} endpoint with a name containing spaces."""
    response = client.get("/hello/John%20Doe")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, John Doe!"}

def test_hello_valid_name_with_special_chars():
    """Test the /hello/{name} endpoint with special characters."""
    response = client.get("/hello/Jean-Pierre")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Jean-Pierre!"}

def test_hello_valid_name_with_numbers():
    """Test the /hello/{name} endpoint with numbers."""
    response = client.get("/hello/User123")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, User123!"}

def test_hello_invalid_empty_string():
    """Test the /hello/{name} endpoint with empty string."""
    response = client.get("/hello/   ")
    assert response.status_code == 400
    assert "Name cannot be empty" in response.json()["detail"]

def test_hello_invalid_whitespace_only():
    """Test the /hello/{name} endpoint with whitespace-only name."""
    response = client.get("/hello/   ")
    assert response.status_code == 400
    assert "Name cannot be empty" in response.json()["detail"]

def test_hello_missing_parameter():
    """Test the /hello/{name} endpoint with missing parameter."""
    response = client.get("/hello/")
    assert response.status_code == 404

def test_palette_valid_keyword():
    """Test the /palette endpoint with a valid keyword."""
    response = client.get("/palette?s=sunset")
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "seed" in data
    assert "colors" in data
    assert "keywords" in data
    
    # Check seed
    assert data["seed"] == "sunset"
    
    # Check colors (5 hex colors)
    assert len(data["colors"]) == 5
    for color in data["colors"]:
        assert color.startswith("#")
        assert len(color) == 7  # #RRGGBB format
        # Verify it's a valid hex color
        assert all(c in "0123456789abcdef" for c in color[1:])
    
    # Check keywords (5 related keywords)
    assert len(data["keywords"]) == 5
    expected_keywords = ["sunset", "sunset-vibe", "sunset-soft", "sunset-bold", "sunset-contrast"]
    assert data["keywords"] == expected_keywords

def test_palette_blank_parameter():
    """Test the /palette endpoint with blank/whitespace parameter."""
    response = client.get("/palette?s=")
    assert response.status_code == 422
    assert response.json()["detail"] == "s must not be blank"

def test_palette_whitespace_parameter():
    """Test the /palette endpoint with whitespace-only parameter."""
    response = client.get("/palette?s=   ")
    assert response.status_code == 422
    assert response.json()["detail"] == "s must not be blank"

def test_palette_missing_parameter():
    """Test the /palette endpoint with missing parameter."""
    response = client.get("/palette")
    assert response.status_code == 422

def test_palette_deterministic():
    """Test that the palette is deterministic for the same keyword."""
    response1 = client.get("/palette?s=test")
    response2 = client.get("/palette?s=test")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json() == response2.json()

def test_root_endpoint():
    """Test the root endpoint returns HTML page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Color Palette Generator" in response.text
    assert "<title>Color Palette Generator</title>" in response.text