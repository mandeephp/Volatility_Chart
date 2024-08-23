# Volatility Chart

**Volatility Chart** is a Django application designed for analyzing and visualizing financial data. It supports importing data from CSV files, calculating financial indicators, and providing interactive charts.

## Features

- Import financial data from CSV files.
- Calculate financial indicators.
- Visualize data with interactive charts.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/mandeephp/Volatility_Chart.git
    cd Volatility_Chart
    ```

2. **Set up a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations:**

    ```bash
    python manage.py migrate
    ```

5. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## Usage

- Open your browser and go to `http://127.0.0.1:8000/` to access the application.

## Configuration

- Ensure your CSV files match the expected format for importing data.

## Development

- To contribute or make changes, create a new branch, make your changes, and submit a pull request.

## Acknowledgments

- Django for providing the web framework.
- Plotly or other libraries for charting (if used).
