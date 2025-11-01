import pandas as pd
import logging

log = logging.getLogger(__name__)

class DataAnalyzer:
    """
    Performs analysis on the enriched product and user data.
    """

    def analyze(self, enriched_df: pd.DataFrame) -> dict:
        if enriched_df.empty:
            log.warning("DataAnalyzer received an empty DataFrame. Returning empty analysis.")
            return {}
        
        log.info("Analyzing data to give seller performance report...")
        enriched_df["username"] = enriched_df["username"].fillna("Unknown Seller")

        aggregations = {
            "revenue": "sum",
            "id": "count",
            "price": "mean"
        }

        #Group by seller and aggregate
        try:
            seller_analysis_df = enriched_df.groupby("username").agg(aggregations)
        except Exception as e:
            log.error(f"Failed to analyze data: {e}")
            return {}
        
        # Rename columns for the final report
        seller_analysis_df = seller_analysis_df.rename(columns={
            'revenue': 'total_revenue',
            'id': 'products_sold',
            'price': 'average_product_price'
        })
        seller_analysis_df = seller_analysis_df.round(2) #round numerical values
        report = seller_analysis_df.to_dict(orient="index")

        log.info(f"Analysis complete. Generated report for {len(report)} sellers")
        return report