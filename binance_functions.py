from csv import writer
from binance.client import Client
import datetime as dt
import os
import math

# API Variables
api_key = os.environ.get("binance_key")
api_secret = os.environ.get("binance_secret")
client = Client(api_key, api_secret)

# log trades
def csv_append(filename, data):
    """Appends data to a csv file."""
    with open (filename, "a+", newline="") as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(data)

# get balance
def get_balance(currency):
    """Returns the free balance of specified currency."""
    balance = client.get_asset_balance(asset = currency)
    balance = float(balance["free"])
    return balance

# buy/sell decimal precision
def get_precision(ticker):
    """Returns the order precision for specified ticker."""
    stepSize = client.get_symbol_info(symbol = ticker)
    stepSize = float(stepSize["filters"][2]["stepSize"])
    precision = int(round(-math.log(stepSize, 10), 0))
    return precision

def truncate(balance, precision):
    """Returns a non-rounded truncated float for specified decimal places."""
    factor = 10.0 ** precision
    return math.trunc(balance * factor) / factor

# get price
def get_price(ticker):
    """Returns most recent trade price for specifed ticker."""
    price = client.get_symbol_ticker(symbol = ticker)
    price = float(price["price"])
    return price

# get last trade
def calc_trade(order):
    trades = order["fills"]
    side = order["side"]
    eth = 0
    usdt = 0
    comm = 0
    for n in trades:
        eth += float(n["qty"])
        usdt += (float(n["qty"]) * float(n["price"]))
        comm += float(n["commission"])
    price = usdt / eth
    if side == "BUY":
        AUD_price = get_price("ETHAUD")
        AUD_total = round(eth * AUD_price, 2)
    elif side == "SELL":
        AUD_price = get_price("AUDUSDT")
        AUD_total = round(usdt / AUD_price)
    AUD_comm = round(get_price("BNBAUD") * comm, 2)
    return dt.datetime.now(), side, eth, price, usdt, comm, AUD_price, AUD_total, AUD_comm

# buy function
def buy(ticker, currency):
    """Places a market buy order for specified ticker.
    Requires quote currency.
    Returns a tuple containing the action "BUY", order quantity, traded price, cost minus fee, and the fee"""
    balance = get_balance(currency)
    order = client.order_market_buy(symbol = ticker, quoteOrderQty = balance)
    trade = calc_trade(order)
    return trade

# sell function
def sell(ticker, currency):
    """Places a market sell order for specified ticker.
    Requires base currency.
    Returns a tuple containing the action "SELL", order quantity, traded price, cost minus fee, and the fee"""
    precision = get_precision(ticker)
    balance = truncate(get_balance(currency), precision)
    order = client.order_market_sell(symbol = ticker, quantity = balance)
    trade = calc_trade(order)
    return trade