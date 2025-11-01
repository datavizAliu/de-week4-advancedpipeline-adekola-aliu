import requests
import logging
from requests.exceptions import RequestException
from pipeline.config import ConfigManager

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class APIClient:
    """
    
    Handles all communication with the Fake store API
    """

    def __init__(self, config_manager: ConfigManager):
        """
        
        """
        try:
            self.base_url = config_manager.get("API","base_url")
            self.limit = int(config_manager.get("API", "pagination_limit"))
        except Exception as e:
            log.error(f"Failed to read API config.Make sure 'base_url' and 'pagination_limit' are in pipeline.cfg: {e}")
            raise
    
    def _make_request(self, endpoint:str, params:dict = None) -> list | dict | None:
        """
        A private helper method to handle all GET requests and error handling.
        """
        url = f"{self.base_url/endpoint}"
        try:
            response  = requests.get(url, params=params)
            #raise error for 4xxx and 5xx
            response.raise_for_status()
            #return JSON data if successful
            return response.json()
        except RequestException as e:
            #network error, connection timeouts, and bad HTTP statuses
            log.error(f"API request failed {url} with params {params}: {e}")
            return None
        except Exception as e:
            #any other unexpected error
            log.error(f"An unexpected error occurred for {url}: {e}")
            return None
        
    def get_all_users(self) -> list[dict]:
        """
        Fetches the complete list of users from /users endpoint.
        """
        log.info("Fetching all users..")
        users = self._make_request(endpoint="users")

        if users is None:
            log.warning("No user data was fetched; returning empty list.")
            return []
        log.info(f"Successfully fetched {len(users)} users")
        return users
    
    def get_all_products(self) -> list[dict]:
        """
        Fetches all products, handling pagination.
        
        This method demonstrates pagination logic by using an 'offset' 
        that increments by 'limit' on each loop.
        
        The loop stops when the API returns an empty list [].
        """
        log.info(f"Fetching all products with pagination (limit={self.limit})...")
        all_products = []
        offset = 0

        while True:
            log.info(f"Fetching products with offsets={offset}...")
            params = {
                'limit': self.limit,
                'offset': offset #pagination
            }

            product_page = self._make_request(endpoint="products", params=params)
            #request failed
            if product_page is None:
                log.error("API request failed during pagination. Stopping fetch.")
                break

            #request succeeded but return  and empty list []

            if not product_page:
                log.info("No more products found. Pagination complete.")
                break

            #we got data, continue
            all_products.extend(product_page) #extend not append
            offset +=self.limit #Increment the offset for the next loop
        log.info(f"successfully fetched a total pf {len(all_products)} products.")
        return all_products


