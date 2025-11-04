import json
import logging
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
            products = self.api_client.get_all_products()
            users = self.api_client.get_all_users()
            
            if not products:
                log.warning("No products fetched. Aborting pipeline.")
                return

            #TRANSFORM
            log.info("--- Starting ETL Pipeline: TRANSFORM Phase ---")
            enriched_data = self.enricher.enrich_data(products, users)
            
            if enriched_data.empty:
                log.warning("Enrichment resulted in empty data. Aborting pipeline.")
                return

            #ANALYZE (and LOAD)
            log.info("--- Starting ETL Pipeline: ANALYZE/LOAD Phase ---")
            report = self.analyzer.analyze(enriched_data)
            
            #Load: Save the report to a JSON file
            with open(self.output_file, 'w') as f:
                json.dump(report, f, indent=4)
                
            log.info(f"--- Pipeline SUCCEEDED. Report saved to {self.output_file} ---")

        except Exception as e:
            log.exception(f"--- Pipeline FAILED: {e} ---")