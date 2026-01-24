import json
import logging
import pandas as pd
from omnicart_pipeline.pipeline.config import ConfigManager
from omnicart_pipeline.pipeline.api_client import APIClient
from omnicart_pipeline.pipeline.data_enricher import DataEnricher
from omnicart_pipeline.pipeline.data_analyzer import DataAnalyzer

log = logging.getLogger(__name__)

class Pipeline:
    """
    Orchestrates the entire ETL (Extract, Transform, Load/Analyze) process.
    """
    
    def __init__(self, config_path: str = 'pipeline.cfg'):
        """
        Initializes all necessary components.
        
        Args:
            config_path: The path to the configuration file.
        """
        try:
            log.info(f"Initializing pipeline with config from: {config_path}")
            self.config = ConfigManager(config_path)
            self.api_client = APIClient(self.config)
            self.enricher = DataEnricher()
            self.analyzer = DataAnalyzer()
            self.output_file = "seller_performance_report.json"
        except Exception as e:
            log.exception(f"Failed to initialize pipeline: {e}")
            raise

    def run(self):
        """
        Executes the full pipeline:
        1. Extract: Fetch data from all API endpoints.
        2. Transform: Join, clean, and enrich the data.
        3. Analyze/Load: Analyze the data and save the report to a file.
        """
        try:
            #EXTRACT
            log.info("--- Starting ETL Pipeline: EXTRACT Phase ---")
            self.api_client.fetch_all_data()
            users = self.api_client.get_all_users()
            products = self.api_client.get_all_products()
            if not users:
                log.warning("No users fetched. Enrichment may be incomplete.")
            

            #TRANSFORM
            log.info("--- Starting ETL Pipeline: TRANSFORM Phase (in pages)---")
            
            all_enriched_dataframes = []

            for cart_page in self.api_client.get_paginated_carts(): 
                log.info(f"Processing page with {len(cart_page)} carts...")
                
                # Enrich just this page of carts,
                # but pass the *full* lookup tables for products and users
                enriched_page_df = self.enricher.enrich_data(cart_page, products, users)
                
                all_enriched_dataframes.append(enriched_page_df)
            if not all_enriched_dataframes:
                log.warning("No data processed. Aborting pipeline.")
                return
            # Combine all the small DataFrames into one big one
            log.info("Consolidating all processed pages...")
            final_enriched_df = pd.concat(all_enriched_dataframes, ignore_index=True)
            
            if final_enriched_df.empty:
                log.warning("Enrichment resulted in empty data. Aborting pipeline.")
                return
            #ANALYZE (and LOAD)
            log.info("--- Starting ETL Pipeline: ANALYZE/LOAD Phase ---")
            report = self.analyzer.analyze(final_enriched_df)
            
            #Load: Save the report to a JSON file
            with open(self.output_file, 'w') as f:
                json.dump(report, f, indent=4)
                
            log.info(f"--- Pipeline SUCCEEDED. Report saved to {self.output_file} ---")

        except Exception as e:
            log.exception(f"--- Pipeline FAILED: {e} ---")