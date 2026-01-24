import pytest
from requests.exceptions import RequestException
from unittest.mock import MagicMock, call
from omnicart_pipeline.pipeline.config import ConfigManager
from omnicart_pipeline.pipeline.api_client import APIClient

#base url the fake config will return
FAKE_BASE_URL = "https://test.api.com"
FAKE_PAGINATION_LIMIT = 2

@pytest.fixture
def mock_config_manager(mocker) -> ConfigManager:
    """
    Creates a mock ConfigManager that doesn't need a real file.
    We patch (mocker.patch) the class itself to control its 'get' method.
    """
    mock_config = mocker.patch('omnicart_pipeline.pipeline.config.ConfigManager').return_value

    def get_side_effect(section, key):
        if section == "API" and key == "base_url":
            return FAKE_BASE_URL
        if section == "API" and key == "pagination_limit":
            return FAKE_PAGINATION_LIMIT
        return None
    mock_config.get.side_effect = get_side_effect
    return mock_config

@pytest.fixture
def api_client(mock_config_manager) -> APIClient:
    """
    Provides an APIClient instance that is pre-configured with the
    mock_config_manager. All tests will use this fixture.
    """
    return APIClient(mock_config_manager)

def test_fetch_all_data(mocker, api_client):
    """
    Tests that fetch_all_data calls the API for products and users
    and correctly populates the internal caches.
    """
    # Arrange
    fake_products = [{"id": 1}, {"id": 2}]
    fake_users = [{"id": 10}, {"id": 20}]
    fake_carts = [{"id": 100}]

    # Mock requests.get to return different data based on URL
    def get_side_effect(url, params=None):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        if "products" in url:
            mock_resp.json.return_value = fake_products
        elif "users" in url:
            mock_resp.json.return_value = fake_users
        elif "carts" in url: 
            mock_resp.json.return_value = fake_carts
        else:
            mock_resp.json.return_value = []
        return mock_resp
    mock_get = mocker.patch("requests.get", side_effect = get_side_effect)
    #Act
    api_client.fetch_all_data()

    #Asssert
    assert mock_get.call_count == 3
    mock_get.assert_has_calls([
         call(f"{FAKE_BASE_URL}/products"),
         call(f"{FAKE_BASE_URL}/users"),
         call(f"{FAKE_BASE_URL}/carts")
    ])
    # 2. Check if caches are now populated
    assert api_client._products_cache == fake_products
    assert api_client._users_cache == fake_users
    assert api_client._carts_cache == fake_carts



def test_get_paginated_carts_generator(api_client):
    """
    Tests that the generator slices the cache correctly.
    This test does NOT need any network mocks.
    """
    # Arrange: Manually set the cache with 5 items.
    # Our limit is 2, so this should create 3 pages: [1,2], [3,4], [5]
    api_client._carts_cache = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]
    
    # Act: Call the generator and convert its output to a list
    pages = list(api_client.get_paginated_carts())
    
    # Assert
    # 1. Should be 3 pages
    assert len(pages) == 3
    
    # 2. Check the content of each page
    assert pages[0] == [{"id": 1}, {"id": 2}]
    assert pages[1] == [{"id": 3}, {"id": 4}]
    assert pages[2] == [{"id": 5}]

def test_get_paginated_carts_empty_cache(api_client):
    """
    Tests that the generator handles an empty cache gracefully.
    """
    # Arrange: Cache is left empty
    
    # Act
    pages = list(api_client.get_paginated_carts())
    
    # Assert
    assert len(pages) == 0