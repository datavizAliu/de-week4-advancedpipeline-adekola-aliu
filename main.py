import logging
from omnicart_pipeline.pipeline.pipeline import Pipeline

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """
    Main entry point for the application.
    """
    log = logging.getLogger(__name__)
    log.info("Application starting...")
    
    try:
        pipeline = Pipeline(config_path='pipeline.cfg')
        pipeline.run()
    except Exception as e:
        log.error(f"Application failed to run: {e}")

if __name__ == "__main__":
    main()