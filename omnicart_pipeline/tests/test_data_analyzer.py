import pytest
import pandas as pd
import numpy as np
from omnicart_pipeline.pipeline.data_analyzer import DataAnalyzer

@pytest.fixture
def sample_enriched_data() -> pd.DataFrame:
    """
    Provides a sample enriched DataFrame to test aggregations.
    """
    data = {
        # 'id' and 'price' would come from the product
        'id': [1, 2, 3, 4],
        'price': [100.00, 50.00, 200.00, 25.00],
        # 'username' would be joined from users
        'username': ['johnd', 'johnd', 'janed', np.nan],
        # 'revenue' would be calculated by the enricher
        'revenue': [1000.00, 250.00, 600.00, 50.00]
    }
    return pd.DataFrame(data)

@pytest.fixture
def analyzer() -> DataAnalyzer:
    """
    Returns an instance of the DataAnalyzer.
    """
    return DataAnalyzer()


def test_analyze_success(analyzer, sample_enriched_data):
    """
    Tests that the analyzer correctly aggregates the data.
    """
    # Act
    report = analyzer.analyze(sample_enriched_data)

    # Assert
    assert isinstance(report, dict)
    
    # Check that both known sellers and the 'Unknown Seller' are present
    assert 'johnd' in report
    assert 'janed' in report
    assert 'Unknown Seller' in report

    # --- Verify 'johnd's' data ---
    # Total Revenue: 1000.00 + 250.00 = 1250.00
    # Products Sold: 2
    # Avg Price: (100.00 + 50.00) / 2 = 75.00
    assert report['johnd']['total_revenue'] == 1250.00
    assert report['johnd']['products_sold'] == 2
    assert report['johnd']['average_product_price'] == 75.00

    # --- Verify 'janed's' data ---
    # Total Revenue: 600.00
    # Products Sold: 1
    # Avg Price: 200.00 / 1 = 200.00
    assert report['janed']['total_revenue'] == 600.00
    assert report['janed']['products_sold'] == 1
    assert report['janed']['average_product_price'] == 200.00

    # --- Verify 'Unknown Seller's' data (from np.nan) ---
    # Total Revenue: 50.00
    # Products Sold: 1
    # Avg Price: 25.00 / 1 = 25.00
    assert report['Unknown Seller']['total_revenue'] == 50.00
    assert report['Unknown Seller']['products_sold'] == 1
    assert report['Unknown Seller']['average_product_price'] == 25.00


def test_analyze_empty_dataframe(analyzer):
    """
    Tests that the analyzer handles an empty DataFrame gracefully.
    """
    # Arrange
    empty_df = pd.DataFrame(columns=['id', 'price', 'username', 'revenue'])
    
    # Act
    report = analyzer.analyze(empty_df)
    
    # Assert
    assert report == {} # Should return an empty dictionary