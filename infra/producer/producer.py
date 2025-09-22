#import requirements
import time
import json
import requests
from kafka import KafkaProducer

# Define variables for API
API_KEY = "enter_your_api_key"  
BASE_URL = "https://finnhub.io/api/v1/quote"
SYMBOLS = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA", "JPM", "META", "V", "PG", "PFE", "CSCO", "IBM", "ORCL", "ADBE", "QCOM"
           , "PYPL", "NFLX", "AMD", "TXN", "UNH", "ABBV", "SBUX", "NKE", "COST", "LOW", "TGT", "BA"] 

# Initialize Producer
producer = KafkaProducer(
    bootstrap_servers=["host.docker.internal:29092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Retrieve Data 
def fetch_quotes(symbol):
    url = f"{BASE_URL}?symbol={symbol}&token={API_KEY}"
    try:
        response = requests.get(url)
        print(f"Response for {symbol}: {response.text}") 
        response.raise_for_status()
        data = response.json()
        if not data or "error" in data:
            print(f"Invalid data for {symbol}: {data}")
            return None
        data["symbol"] = symbol
        data["fetched_at"] = int(time.time())
        return data
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error fetching {symbol}: {e.response.text}")
        return None
    except ValueError as e:
        print(f"JSON Decode Error for {symbol}: {e} - Response: {response.text}")
        return None
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

# Continuos Looping for Streaming data
while True:
    for symbol in SYMBOLS:
        quote = fetch_quotes(symbol)
        if quote:
            print(f"Producing: {quote}")
            producer.send("stock-quotes", value=quote)
    time.sleep(6) 