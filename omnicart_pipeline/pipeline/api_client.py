import requests
import logging
from requests.exceptions import RequestException
from omnicart_pipeline.pipeline.config import ConfigManager  # Assuming config.py is in the same folder

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class APIClient:
    """
    Handles all communication with the Fake Store API.
    .
    """
    def __init__(self, config_manager: ConfigManager):
        try:
            self.base_url = config_manager.get('API', 'base_url')
            self.limit = int(config_manager.get('API', 'pagination_limit'))
            
            # Caches to store the *complete* data set
            self._products_cache = []
            self._users_cache = []
            self._carts_cache = []
        except Exception as e:
            log.error(f"Failed to read API config: {e}")
            raise

    def _make_request(self, endpoint: str) -> list | dict | None:
        """
        Private helper to make a single, non-paginated GET request.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url)
            response.raise_for_status() 
            return response.json()
        except RequestException as e:
            log.error(f"API request failed for {url}: {e}")
            return None

    def fetch_all_data(self):
        """
        Fetches ALL products and users from the API *once*
        and stores them in the local cache.
        This must be called before getting paginated data.
        """
        log.info("Fetching all products from API...")
        products = self._make_request(endpoint="products")
        if products:
            self._products_cache = products
            log.info(f"Successfully cached {len(self._products_cache)} products.")
        else:
            log.warning("Failed to fetch products.")
            
        log.info("Fetching all users from API...")
        users = self._make_request(endpoint="users")
        if users:
            self._users_cache = users
            log.info(f"Successfully cached {len(self._users_cache)} users.")
        else:
            log.warning("Failed to fetch users.")

        log.info("Fetching all carts from API...")  # <-- ADD THIS BLOCK
        carts = self._make_request(endpoint="carts")
        if carts:
            self._carts_cache = carts
            log.info(f"Successfully cached {len(self._carts_cache)} carts.")
        else:
            log.warning("Failed to fetch carts.")

    def get_all_users(self) -> list[dict]:
        """
        Returns the complete list of users from the cache.
        """
        if not self._users_cache:
            log.warning("User cache is empty. Was fetch_all_data() called?")
        return self._users_cache
    
    def get_all_products(self) -> list[dict]: 
        """
        Returns the complete list of products from the cache.
        """
        if not self._products_cache:
            log.warning("Product cache is empty. Was fetch_all_data() called?")
        return self._products_cache

    def get_paginated_carts(self) -> iter:
        """
        A generator that *yields* pages of carts
        from the local cache based on the pagination limit.
        """
        if not self._carts_cache: 
            log.warning("Cart cache is empty. Was fetch_all_data() called?")
            return
            
        log.info(f"Paginating cached carts into chunks of {self.limit}...")
        
    
        for i in range(0, len(self._carts_cache), self.limit):
            yield self._carts_cache[i : i + self.limit]
            
        log.info("Finished paginating all carts.")