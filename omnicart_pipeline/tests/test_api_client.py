import pytest
import requests
from requests.exceptions import RequestException
from unittest.mock import MagicMock, call
from omnicart_pipeline.pipeline.config import ConfigManager
from omnicart_pipeline.pipeline.api_client import APIClient

#base url the fake config will return
FAKE_BASE_URL = "https://test.api.com"
FAKE_PAGINATION_LIMIT = 5

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
    mock_config.side_effect = get_side_effect
    return mock_config

@pytest.fixture
def api_client(mock_config_manager) -> APIClient:
    """
    Provides an APIClient instance that is pre-configured with the
    mock_config_manager. All tests will use this fixture.
    """
    return APIClient(mock_config_manager)

def test_get_all_users_success(mocker, api_client):
    """
    Tests that get_all_users calls the correct URL and returns the data
    on a successful API call.
    """
    # Arrange: Create fake data and a mock response
    fake_users = [{"id": 1, "name": "Test User"}]
    mock_response = MagicMock()
    mock_response.json.return_value = fake_users
    mock_response.raise_for_status = MagicMock() # Does nothing, i.e., "success"

    mock_get = mocker.patch("requests.get", return_value = mock_response)

    users = api_client.get_all_users()

    assert users == fake_users # Assert: Check the results
    mock_get.assert_called_once() # Check that requests.get was called exactly once
    mock_get.asser_called_with(f"{FAKE_BASE_URL}/users", params=None) # Check that it was called with the correct URL and no params


def test_get_all_users_failure(mocker, api_client):
        """
        Tests that get_all_users returns an empty list if the API request fails.
        """
        #Arrange
        mock_get = mocker.patch("requests.get", side_effect = RequestException("Test network error"))

        #Act
        users = api_client.get_all_users()

        #Assert

        assert users == [] #Should fail
        mock_get.assert_called_once()

def test_get_all_products_pagination(mocker, api_client):
        """
        This is the most important test.
        It proves the pagination loop works, stops correctly, and concatenates results.
        """

        #Arrange
        page_1_data = [{"id": 1}, {"id":2}] #page 1 with 2 products
        page_2_data = []

        #Mock responses for each page
        mock_response_page_1 = MagicMock()
        mock_response_page_1.json.return_value = page_1_data
        mock_response_page_1.raise_for_status = MagicMock()

        mock_response_page_2 = MagicMock()
        mock_response_page_2.json.return_value = page_2_data
        mock_response_page_2.raise_for_status = MagicMock()
        
        #Patch requests.get to return page 1 first, then page 2
        mock_get = mocker.patch('requests.get', side_effect=[mock_response_page_1, mock_response_page_2])
        
        #Act 
        products = api_client.get_all_products()

        #Assert
        #did we get the right final data?
        assert products == page_1_data

        #did it call the API exactly twice? (once for page 1, once for the empty page)
        assert mock_get.call_count == 2

        # expected_calls = [
        #     #call 1: offset=0
        #     call(f"{FAKE_BASE_URL}/products", params={'limit': FAKE_PAGINATION_LIMIT, 'offset': 0}),
        #     # Call 2: offset=5 (0 + 5)
        #     call(f"{FAKE_BASE_URL}/products", params={'limit': FAKE_PAGINATION_LIMIT, 'offset': FAKE_PAGINATION_LIMIT}),
        # ]
        # mock_get.assert_has_calls(expected_calls)
    
def test_get_all_products_failure_during_pagination(mocker, api_client):
    """
    Tests that if an error happens *during* pagination, we still
    return an empty list (or you could decide to return what you have so far,
    but returning [] is a simpler, safer failure mode).
    """
    #Arrange
    mock_get = mocker.patch('requests.get', side_effect=RequestException("Test network error"))

    # Act
    products = api_client.get_all_products()

    # Assert
    assert products == [] # Should fail gracefully
    mock_get.assert_called_once() # Should stop after the first failed call
