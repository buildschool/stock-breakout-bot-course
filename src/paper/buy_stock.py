# Import Screener
from finviz.screener import Screener
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import warnings
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import dotenv_values
import math
import filter_by_ta
import os

# Define prod config
config = os.environ

# # Define dev config
# config = dotenv_values(".env")

# Init the Trading Client
trading_client = TradingClient(config['ALPACA_API_KEY'], config['ALPACA_SECRET_KEY'], paper=True)

# Define the timeframes
tf = {
    "interval": "1d",
    "period": "1y"
}

# Ignore Warnings
warnings.filterwarnings("ignore")

# Get Data
def get_data():
    filters = ['sh_relvol_o1.5', 'ta_change_u5', 'ta_sma50_cross200a', 'ta_volatility_wo5']
    stock_list = Screener(filters=filters, table="Technical", order="-Change")
    return stock_list

# Get account information
def get_account():
    account = trading_client.get_account()
    return account.cash

# Define 10% of my account cash value
def trade_amount(cash):
    cash = int(float(cash))
    out = math.floor(cash/10)
    return out

# Buy function
def buy(ticker, qty):
    market_order_request = MarketOrderRequest(
        symbol=ticker,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
    market_order = trading_client.submit_order(
        order_data=market_order_request
    )
    return market_order

# Print stock list
def main():
    stocks_to_trade = []
    stocks = get_data()
    for stock in stocks:
        tick = yf.Ticker(stock['Ticker'])
        hist = tick.history(interval=tf['interval'], period=tf['period'])
        buy_or_sell = False
        macd = {}
        vwap = {}
        rsi = {}
        try:
            macd = ta.macd(hist['Close'])
            rsi = ta.rsi(hist['Close'], length=14)
            vwap = ta.vwap(hist['High'], hist['Low'], hist['Close'], hist['Volume'])
        except:
            print('error with', stock['Ticker'])
            pass
        try:
            buy_or_sell = filter_by_ta.filter_by_ta(stock, hist, macd, vwap, rsi)
            if buy_or_sell == True:
                stocks_to_trade.append({"Symbol":stock['Ticker'], "price":stock['Price']})
        except:
            print('error with', stock['Ticker'])
    account = get_account()
    out = trade_amount(account)
    qty = math.floor(out / float(stocks_to_trade[0]['price']))
    order = buy(stocks_to_trade[0]['Symbol'], qty)
    if order.client_order_id:
        print("Order Successful", stocks_to_trade[0]['Symbol'])
    else:
        print("Order not successful", stocks_to_trade[0]['Symbol'])
    return order

# Run main    
main()