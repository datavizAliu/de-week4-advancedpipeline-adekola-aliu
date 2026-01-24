import pytest
import pandas.testing as pd_testing
import pandas as pd
from unittest.mock import MagicMock, patch

from omnicart_pipeline.pipeline.pipeline import Pipeline

@pytest.fixture
def mock_config_manager(mocker) -> MagicMock:
    """
    Mocks the configManager class.
    """
    # mock = mocker.patch('omnicart_pipeline.pipeline.pipeline.APIClient').return_value
    # # Set up mock return values for its methods
    # mock.get_all_products.return_value = [{"id": 1, "userId": 1}]
    # mock.get_all_users.return_value = [{"id": 1, "username": "testuser"}]
    # return mock
    mock_config = mocker.patch('omnicart_pipeline.pipeline.config.ConfigManager').return_value
    def get_side_effect(section, key):
        if section == "API" and key == "base_url":
            return "https://fake.com"
        if section == "API" and key == "pagination_limit":
            return 5
        return None
    mock_config.get.side_effect = get_side_effect
    return mock_config

@pytest.fixture
def mock_api_client(mocker) -> MagicMock:
    """Mocks the APIClient class."""
    mock = mocker.patch('omnicart_pipeline.pipeline.pipeline.APIClient').return_value
    # Set up mock return values for its methods
    mock.get_all_products.return_value = [{"id": 1, "price": 10}]
    mock.get_all_users.return_value = [{"id": 1, "username": "testuser"}]

    mock_cart_page = [{"id": 1, "userId": 1, "products": [{"productId": 1, "quantity": 2}]}]
    # Make the mock generator return a list containing this one page
    mock.get_paginated_carts.return_value = [mock_cart_page]
    return mock

@pytest.fixture
def mock_enricher(mocker) -> MagicMock:
    """Mocks the DataEnricher class."""
    mock = mocker.patch('omnicart_pipeline.pipeline.pipeline.DataEnricher').return_value
    # Set up a mock DataFrame to return
    mock.enrich_data.return_value = pd.DataFrame({"id": [1], "username": ["testuser"]})
    return mock

@pytest.fixture
def mock_analyzer(mocker) -> MagicMock:
    """Mocks the DataAnalyzer class."""
    mock = mocker.patch('omnicart_pipeline.pipeline.pipeline.DataAnalyzer').return_value
    # Set up a mock report to return
    mock.analyze.return_value = {"testuser": {"products_sold": 1}}
    return mock

@pytest.fixture
def mock_open(mocker) -> MagicMock:
    """Mocks the built-in 'open' function to test file writing."""
    # We patch 'open' in the pipeline module's namespace
    return mocker.patch('omnicart_pipeline.pipeline.pipeline.open')

#Orchestration test

def test_pipeline_run_orchestration(
        mock_config_manager,
        mock_api_client,
        mock_enricher,
        mock_analyzer,
        mock_open
):
    """
    Tests that the pipeline.run() method calls each component
    in the correct order and with the correct data.
    """

    #Arrange

    #Act
    pipeline = Pipeline(config_path="fake_path.cfg")
    pipeline.run() 

    #Assert
    mock_api_client.fetch_all_data.assert_called_once() # Good
    mock_api_client.get_all_products.assert_called_once()
    mock_api_client.get_all_users.assert_called_once()
    mock_api_client.get_paginated_carts.assert_called_once()

    mock_enricher.enrich_data.assert_called_once_with(
        mock_api_client.get_paginated_carts.return_value[0], #first (and only) cart page
        mock_api_client.get_all_products.return_value,      #full list of products
        mock_api_client.get_all_users.return_value          #full list of users
    )

    mock_analyzer.analyze.assert_called_once()
    
    actual_call_args = mock_analyzer.analyze.call_args[0]
    
    #Check it was called with one argument
    assert len(actual_call_args) == 1
    
    #Get the DataFrame that was passed
    passed_df = actual_call_args[0]
    
    expected_df = pd.concat([mock_enricher.enrich_data.return_value], ignore_index=True)
    pd_testing.assert_frame_equal(passed_df, expected_df)
    
    mock_open.assert_called_once_with("seller_performance_report.json", "w")