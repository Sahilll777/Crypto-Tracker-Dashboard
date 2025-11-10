import requests
import pandas as pd

BASE_URL = "https://api.coingecko.com/api/v3"

def get_supported_coins():
    """Return list of all supported coins."""
    url = f"{BASE_URL}/coins/list"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_market_data(vs_currency="usd", per_page=10, page=1):
    """Fetch top N coins market data."""
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_price_chart(coin_id, vs_currency="usd", days=1):
    """Fetch market chart data for given coin."""
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df
