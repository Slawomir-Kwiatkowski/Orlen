import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def fetch_data(product_id, current_date):
    url = (
        f"https://tool.orlen.pl/api/wholesalefuelprices/"
        f"ByProduct?productId={product_id}"
        f"&from=2000-01-01"
        f"&to={current_date}"
    )
    try:
        response = requests.get(url)
    except requests.RequestException:
        return None
    else:
        return response.json()


def json_to_df(data):
    df = pd.json_normalize(data)
    df = df[["effectiveDate", "value"]]
    df["effectiveDate"] = pd.to_datetime(df["effectiveDate"])
    df["value"] = df["value"].astype(int)
    df.set_index(df["effectiveDate"], inplace=True)
    df.sort_index(inplace=True)
    return df
