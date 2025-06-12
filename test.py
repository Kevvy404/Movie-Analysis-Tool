import pytest
import requests
import requests_mock
from main import get_movie_info, search_movies, get_popular_movies

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = "test_api_key"

@pytest.fixture
def mock_tmdb():
    with requests_mock.Mocker() as m:
        yield m

def test_get_movie_info_success(mock_tmdb):
    movie_id = 550
    mock_data = {
        "id": movie_id,
        "title": "Fight Club",
        "overview": "A movie about...",
        "popularity": 100.0
    }
    mock_tmdb.get(
        f"{BASE_URL}/movie/{movie_id}",
        json=mock_data,
        status_code=200
    )
    
    result = get_movie_info(movie_id)
    
    assert result == mock_data
    assert result["title"] == "Fight Club"
    assert isinstance(result["popularity"], float)

def test_get_movie_info_not_found(mock_tmdb):
    movie_id = 999999
    mock_tmdb.get(
        f"{BASE_URL}/movie/{movie_id}",
        status_code=404
    )
    
    with pytest.raises(requests.exceptions.HTTPError):
        get_movie_info(movie_id)

def test_search_movies_success(mock_tmdb):
    query = "Inception"
    mock_data = {
        "results": [{"title": "Inception"}],
        "total_results": 1
    }
    
    mock_tmdb.get(
        f"{BASE_URL}/search/movie?api_key=test&query=Inception&language=en-UK&page=1",
        json=mock_data,
        status_code=200
    )
    
    mock_tmdb.get(
        f"{BASE_URL}/search/movie",
        json=mock_data,
        status_code=200,
        complete_qs=False
    )
    
    result = search_movies(query)
    assert result["total_results"] == 1

def test_search_movies_empty_query(mock_tmdb):
    mock_tmdb.get(
        f"{BASE_URL}/search/movie",
        json={"results": []},
        status_code=200
    )
    
    result = search_movies("")
    assert len(result["results"]) == 0

def test_get_popular_movies_success(mock_tmdb):
    mock_data = {
        "results": [
            {"id": 1, "title": "Popular Movie 1"},
            {"id": 2, "title": "Popular Movie 2"}
        ],
        "page": 1,
        "total_pages": 1
    }
    
    mock_tmdb.get(
        f"{BASE_URL}/movie/popular",
        json=mock_data,
        status_code=200,
        complete_qs=False 
    )
    
    result = get_popular_movies()

    assert len(result["results"]) == 2
    assert result["page"] == 1
    assert result["results"][0]["title"] == "Popular Movie 1"

def test_api_authentication_failure(mock_tmdb):
    endpoints = [
        (f"{BASE_URL}/movie/550", {"api_key": "test"}),
        (f"{BASE_URL}/search/movie", {"query": "test", "api_key": "test"}),
        (f"{BASE_URL}/movie/popular", {"api_key": "test"})
    ]
    
    for endpoint, params in endpoints:
        mock_tmdb.get(
            endpoint,
            status_code=401,
            json={"status_message": "Invalid API key"},
            complete_qs=False
        )
    
    # Test each function
    with pytest.raises(requests.exceptions.HTTPError):
        get_movie_info(550)
    
    with pytest.raises(requests.exceptions.HTTPError):
        search_movies("test")
    
    with pytest.raises(requests.exceptions.HTTPError):
        get_popular_movies()