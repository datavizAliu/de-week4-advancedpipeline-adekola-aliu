# OmniCart Analytics Pipeline (de-week4-advancedpipeline)

This project is a complete ETL (Extract, Transform, Load) pipeline built with Python. It fetches data from multiple endpoints of the Fake Store API, enriches the product data with seller information, performs analysis on seller performance, and saves the result as a JSON report.

This pipeline is built with a test-driven, component-based design.

---

## 🚀 How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)datavizAliu/de-week4-advancedpipeline-adekola-aliu.git
    cd de-week4-advancedpipeline-adekola-aliu
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows (PowerShell)
    python -m venv .venv
    .\.venv\Scripts\activate.ps1
    
    # On macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the pipeline:**
    ```bash
    python main.py
    ```
    The final report will be saved as `seller_performance_report.json`.

---

## 🛠️ Pipeline Logic

### Pagination Strategy

The `APIClient` handles pagination by using a `while` loop. It makes repeated calls to the `/products` endpoint, using a `limit` parameter (read from `pipeline.cfg`) and an incrementing `offset` parameter. The loop terminates when the API returns an empty list `[]`, which signifies that no more data is available.

### Data Enrichment Logic

The `DataEnricher` module uses `pandas` to perform the "Transform" step.

1.  It converts the raw `products` and `users` lists into two separate DataFrames.
2.  It flattens the nested `rating.count` object into a top-level `quantity` column.
3.  It calculates a `revenue` column (`price` * `quantity`).
4.  It performs a **left merge** (`how='left'`) from the products DataFrame onto the users DataFrame. This matches `products.userId` with `users.id` and adds seller information (like `username`) to each product.
5.  Using a left merge ensures that all products are kept in the dataset, even if their corresponding seller is missing.