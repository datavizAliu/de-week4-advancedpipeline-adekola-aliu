import pytest
import pandas as pd
import numpy as np
from omnicart_pipeline.pipeline.data_enricher import DataEnricher

@pytest.fixture
def sample_products_list() -> list[dict]:
    """Provides a raw list of product dictionaries."""
    return [
        {
            "id": 1,
            "title": "Product A",
            "price": 100.0,
            "userId": 1, # Matches 'johnd'
            "rating": {"rate": 4.0, "count": 10} # revenue = 100 * 10 = 1000
        },
        {
            "id": 2,
            "title": "Product B",
            "price": 50.0,
            "userId": 99, # No matching user
            "rating": {"rate": 3.0, "count": 5} # revenue = 50 * 5 = 250
        }
    ]

@pytest.fixture
def sample_users_list() -> list[dict]:
    """Provides a raw list of user dictionaries."""
    return [
        {
            "id": 1,
            "username": "johnd",
            "email": "johnd@test.com",
            "name": {"firstname": "John", "lastname": "Doe"},
            "address": "123 Main St", # This data should be ignored
            "phone": "555-1234"      # This data should be ignored
        }
        # Note: No user with id 99
    ]

@pytest.fixture
def enricher() -> DataEnricher:
    """Returns an instance of the DataEnricher."""
    return DataEnricher()


def test_successful_join(enricher, sample_products_list, sample_users_list):
    """
    Tests that a product with a marching ID is correctly enriched
    """
    #Act
    enriched_df = enricher.enrich_data(sample_products_list, sample_users_list)

    #Assert
    product_1 = enriched_df[enriched_df["id"]==1].iloc[0]

    assert product_1["username"] == 'johnd'
    assert product_1["email"] == "johnd@test.com"

def test_join_edge_case_missing_user(enricher, sample_products_list, sample_users_list):
    """
    Tests that a product with a non-existent user ID has NaN for user columns.
    This proves the left join worked correctly.
    """
    # Act
    enriched_df = enricher.enrich_data(sample_products_list, sample_users_list)
    
    # Assert
    product_2 = enriched_df[enriched_df['id'] == 2].iloc[0]
    
    # Check that user data is NaN (or NaT for dates, pd.NA for strings)
    # pd.isna() checks for all of them
    assert pd.isna(product_2['username'])
    assert pd.isna(product_2['email'])


def test_revenue_calculation(enricher, sample_products_list, sample_users_list):
    """
    Tests that the 'revenue' column is calculated correctly from 'price' * 'rating.count'.
    """
    # Act
    enriched_df = enricher.enrich_data(sample_products_list, sample_users_list)
    
    # Assert
    assert enriched_df[enriched_df['id'] == 1].iloc[0]['revenue'] == 1000.0
    
    # Check revenue for Product 2 (50.0 * 5)
    assert enriched_df[enriched_df['id'] == 2].iloc[0]['revenue'] == 250.0
