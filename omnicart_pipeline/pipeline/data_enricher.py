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
   
    def enrich_data(self,carts: list[dict], products: list[dict], users: list[dict]) -> pd.DataFrame:
        """
        Enriches cart data with product and user details.
        """
        if not carts or not products or not users:
            log.warning("No data to enrich. Returning empty DataFrame.")
            #return an empty dataframe
            return pd.DataFrame()
        
        try:
            carts_df = pd.DataFrame(carts)
            products_df = pd.DataFrame(products)
            users_df = pd.DataFrame(users)
        except Exception as e:
            log.error(f"failed to created DataFrames from API data: {e}")
            return pd.DataFrame()
        log.info(f"Loaded {len(products_df)} products and {len(users_df)} users into DataFrame")
        
        #Clean & Transform Product Data
        if 'products' not in carts_df.columns:
                log.error("Carts DataFrame has no 'products' column. Cannot proceed.")
                return pd.DataFrame()
                
        sales_df = carts_df.explode('products').reset_index(drop=True)

        sales_df = pd.concat([
            sales_df.drop('products', axis=1), 
            sales_df['products'].apply(pd.Series)
        ], axis=1)
        products_subset = products_df[['id', 'price', 'title']]
        
        enriched_df = pd.merge(
            sales_df,
            products_subset,
            left_on='productId',
            right_on='id',
            how='left',
            suffixes=('_cart', '_product')
        )

        # Now we join the result with users to get seller info.
        users_subset = users_df[['id', 'username']]
        
        enriched_df = pd.merge(
            enriched_df,
            users_subset,
            left_on='userId',
            right_on='id',
            how='left',
            suffixes=('_sale', '_user')
        )

        #revenue calculation
        enriched_df['price'] = pd.to_numeric(enriched_df['price'], errors='coerce')
        enriched_df['quantity'] = pd.to_numeric(enriched_df['quantity'], errors='coerce')
        enriched_df['revenue'] = enriched_df['price'] * enriched_df['quantity']

        log.info("Data enrichment complete.")
        return enriched_df

