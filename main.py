import os
import requests
from prettytable import PrettyTable

# AlphaVantage stock API variables:
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_API_ENDPOINT = "https://www.alphavantage.co/query"
ALPHA_PARAMS = {
    "apikey": ALPHA_VANTAGE_API_KEY,
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
}
# ---------------------------------
# NewsAPI variables:
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
NEW_API_PARAMS = {
    "apiKey": NEWS_API_KEY,
    "language": "en",
    "q": "tesla",
    "from": "2021-05-16",
    "to": "2021-05-16",
}
# ---------------------------------

pretty = PrettyTable()

# getting some news about our stock first:
stock_news = requests.get(NEWS_API_ENDPOINT, NEW_API_PARAMS)
stock_news.raise_for_status()

news_data = stock_news.json()["articles"]
news_data = [{
    "source": item["source"]["name"],
    "datetime": item["publishedAt"],
    "title": item["description"],
} for item in news_data]

# pulling the stock data on historical prices per day:
alpha_stock = requests.get(ALPHA_API_ENDPOINT, ALPHA_PARAMS)
alpha_stock.raise_for_status()

alpha_data = [{
    "date": date,
    "open": stock["1. open"],
    "close": stock["4. close"]}
              for date, stock in alpha_stock.json()["Time Series (Daily)"].items()]

# calculating the price differences from day to day and expanding our stock dict:
for index in range(0, len(alpha_data)):
    if index < len(alpha_data) - 1:
        delta_price = round(float(alpha_data[index]["open"]) - float(alpha_data[index+1]["close"]), 2)
        delta_percent = round((float(alpha_data[index]["open"]) / float(alpha_data[index+1]["close"]) - 1) * 100, 2)
        alpha_data[index].update({"price delta": delta_price, "price percent delta": delta_percent})
    else:
        delta_price = 0
        delta_percent = 0
        alpha_data[index].update({"price delta": delta_price, "price percent delta": delta_percent})
        break

# quick pretty table to display the stock prices and differences through the days:
pretty.title = "Tesla Stock Prices Last 25 Days"
pretty.field_names = ["Date", "Opening Price", "Closing Price", "Price diff. vs. Previous day Close",
                      "% vs. prev. day Close"]
for _ in range(0, len(alpha_data)):
    pretty.add_row([alpha_data[_]["date"], alpha_data[_]["open"], alpha_data[_]["close"],
                    alpha_data[_]["price delta"], str(alpha_data[_]["price percent delta"]) + "%"])

print(pretty)
