import pandas as pd
import logging


log = logging.getLogger(__name__)

class DataEnricher:
    """
    Combines, cleans, and enriches products and user data.
    """
    def _flatten_product_data(self, product_df: pd.DataFrame) -> pd.DataFrame:
        """
        Flattens the nested 'rating' dictionary into top-level columns.
        We assume 'rating.count' is the quantity sold.
        """
        if "rating" in product_df.columns:

            product_df["quantity"] = product_df["rating"].apply(

                lambda r: r.get("count", 0) if isinstance(r, dict) else 0
            )

            product_df["rate"] = product_df["rating"].apply(

                lambda r: r.get("rate", 0.0) if isinstance(r, dict) else 0
            )
        else:

            product_df["quantity"] = 0
            product_df["rate"] = 0.0
        
        return product_df
   
    def enrich_data(self, products: list[dict], users: list[dict]) -> pd.DataFrame:
        """
        
        """
        if not products:
            log.warning("No products to enrich. Returning empty DataFrame.")
            #return an empty dataframe
            return pd.DataFrame()
        
        try:
            products_df = pd.DataFrame(products)

            if not users:
                users_df = pd.DataFrame(columns=["id", "username", "email", "name"])
            else:
                users_df = pd.DataFrame(users)
        except Exception as e:
            log.error(f"failed to created DataFrames from API data: {e}")
            return pd.DataFrame()
        log.info(f"Loaded {len(products_df)} products and {len(users_df)} users into DataFrame")
        
        #Clean & Transform Product Data
        products_df = self._flatten_product_data(products_df)

        #Ensure price is numeric, coercing errors to NaN
        products_df["price"] = pd.to_numeric(products_df["price"], errors='coerce')
        products_df["revenue"] = products_df["price"] * products_df["quantity"]

        #columns we need for join and report
        user_columns = ['id', 'username', 'email', 'name']

        for col in user_columns:
            if col not in users_df.columns:
                users_df[col] = pd.NaT if col == 'id' else pd.NA
        users_df_subset = users_df[user_columns]

        #Left join
        log.info("Enriching product data with user information...")
        enriched_df = pd.merge(
            products_df,
            users_df_subset,
            left_on="userId", #from products_df
            right_on="id",    #from user_df_subset
            how="left",
            suffixes=("_product", "_user")
        )

        #Drop redundant user "id" column from join
        if "id_user" in enriched_df.columns:
            enriched_df = enriched_df.drop(columns=["id_user"])
        #Rename product id 
        if "id_product" in enriched_df.columns:
            enriched_df = enriched_df.rename(columns={"id_product": "id"})

        log.info("Data enrichment complete.")
        return enriched_df

