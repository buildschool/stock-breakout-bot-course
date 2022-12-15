# Import Screener
from finviz.screener import Screener
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import warnings
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import dotenv_values
import math
import filter_by_ta
import os
import check_if_market_open

# Define timeframe
tf = {
    "interval": "1h",
    "period": "1mo"
}

# Define prod config
config = os.environ

# # Define dev config
# config = dotenv_values(".env")

# Init the Trading Client
trading_client = TradingClient(config['ALPACA_API_KEY'], config['ALPACA_SECRET_KEY'], paper=True)

# Get postions
def get_postions():
    positions = trading_client.get_all_positions()
    return positions

# Sell stock
def sell_stock(ticker, qty, price):
    limit_order_request = LimitOrderRequest(
        symbol=ticker,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        limit_price=price
    )
    limit_order = trading_client.submit_order(
        order_data=limit_order_request
    )
    return limit_order

# Define config
def main():
    positions = get_postions()
    if len(positions) > 0:
        for position in positions:
            tick = yf.Ticker(position.symbol)
            hist = tick.history(interval=tf['interval'], period=tf['period'])
            try:
                macd = ta.macd(hist['Close'])
                rsi = ta.rsi(hist['Close'], length=14)
                vwap = ta.vwap(hist['High'], hist['Low'], hist['Close'], hist['Volume'])
            except:
                print('error with', position.symbol)
                pass
            try:
                stock = {
                    "Ticker": position.symbol
                }
                buy_or_sell = filter_by_ta.filter_by_ta(stock, hist, macd, vwap, rsi)
                if buy_or_sell == False:
                    try:
                        out = sell_stock(position.symbol, position.qty, hist.iloc[-1]['Close'])
                        if out.client_order_id:
                            print("Order Request Successful", position.symbol)
                        else:
                            print("Order Request Not Successful", position.symbol)
                    except:
                        print("error with", position.symbol)
            except:
                print('error with', position.symbol)
    return positions

# Run check_if_market_open function
stock_market_open = check_if_market_open.get_if_market_day()

# If market is open check holdings
if stock_market_open:
    main()
else:
    print('Market not open')