import requests
import yahoo_fin.stock_info as si
import json
import pandas as pd
from datetime import timedelta, date
import time
#import requests_cache

payload = {
    'apikey': 'hwP29tTWlVoIdBHp5HSvY5YHWjOenLZA',
}

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def days(n):
    return str(date.today() - timedelta(n))

def get_price(ticker):
    response = requests.get("https://api.polygon.io/v2/aggs/ticker/" + ticker + "/prev?adjusted=true&apiKey=hwP29tTWlVoIdBHp5HSvY5YHWjOenLZA").json()
    price_data = response["results"]
    closingprice = price_data[0]["c"]
    return(closingprice)

def basefunction(ticker, interval1, interval2):
    response = requests.get("https://api.polygon.io/v2/aggs/ticker/" + ticker + "/range/1/day/" + days(interval2) + "/" + days(interval1) + "?adjusted=true&sort=asc&limit=1000&apiKey=hwP29tTWlVoIdBHp5HSvY5YHWjOenLZA").json()
    price_data = response["results"]
    closingprice = price_data[0]["c"]
    openingprice = price_data[(len(price_data) - 1)]["c"]
    return(openingprice, closingprice)


def percent_change(ticker, interval):
    response = requests.get("https://api.polygon.io/v2/aggs/ticker/" + ticker + "/range/1/year/" + days(interval) + "/" + str(date.today()) + "?adjusted=true&sort=asc&limit=1000&apiKey=hwP29tTWlVoIdBHp5HSvY5YHWjOenLZA").json()
    price_data = response["results"]
    closingprice = price_data[0]["c"]
    openingprice = price_data[0]["o"]

    asset_percent_change = (closingprice - openingprice)/openingprice * 100
    time.sleep(20)
    return(asset_percent_change)

def consistent_growth(ticker, intervals):
    stock_prices = []
    stock_prices2 = []
    counter = 0
    j = 0
    while (j < len(intervals)):
        stock_prices.append(basefunction(ticker, intervals[j], intervals[j+1]))
        j += 2
    for i in stock_prices:
        stock_prices2.append(i[0])
        stock_prices2.append(i[1])
    for i in range(len(stock_prices2) - 1):
        if stock_prices2[i] > stock_prices2[i+1]:
            counter += 1
    #if counter >= 6:
       # return 1
   # else:
      #  return 0
    return counter

def simple_moving_average(ticker):
    response = requests.get("https://api.polygon.io/v1/indicators/sma/" + ticker + "?timespan=month&adjusted=true&window=12&series_type=close&order=desc&limit=12&apiKey=hwP29tTWlVoIdBHp5HSvY5YHWjOenLZA").json()
    results = response["results"]
    values = results["values"]
    values_list = []
    counter = 0
    for i in range(len(values) - 1):
        values_list.append(values[i]["value"])
    for i in range(len(values_list) - 1):
        if values_list[i] > values_list[i+1]:
            counter += 1
    if (counter >= 9):
        return True

# Get all tickers in S&P 500
tickers = si.tickers_sp500()
#tickers = ["AAPL", "META", "MSFT", "LLY", "NVDA", "RCL", "BLDR", "UBER", "CCL", "AMD", "PHM"]
#tickers = ["NVDA"]

intervals = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450]

# Get price data for each ticker
df = pd.DataFrame(columns=['Ticker', 'PercentReturn'])

#percent change for S&P500
spy_percent_change = percent_change("SPY", 360)
print(spy_percent_change)
time.sleep(60)
for i in tickers:
    try:
        ticker_percent_change = percent_change(i, 360)
        print(ticker_percent_change)
        if ticker_percent_change > spy_percent_change:
            df = df.append({'Ticker': i, 'PercentReturn': ticker_percent_change}, ignore_index=True)
            print(i + " success")
    except:
        print(i + " failed")
        time.sleep(60)
        #time.sleep(5)
df = df.sort_values(by=['PercentReturn'], ascending=False)
# Getting top 20% of tickers
df = df[df.PercentReturn >= df.PercentReturn.quantile(.80)]
print(df)
# Final Chart of tickers
finaldf = pd.DataFrame(columns=['Ticker', 'PercentReturn', 'Consistency Rating', 'Current Price'])
percent_returns = df["PercentReturn"].tolist()
tickers = df["Ticker"].tolist()
for i in range(len(tickers)):
    current_price = get_price(tickers[i])
    print("Current Price: " + str(current_price))
    percentreturn = percent_returns[i]
    print("Percent Return: " + str(percentreturn))
    time.sleep(60)
    consistency = consistent_growth(tickers[i], intervals)
    time.sleep(60)
    print("Consistency: " + str(consistency))
    condition_1 = simple_moving_average(tickers[i])
    time.sleep(60)
    condition_2 = consistency >= 6
    
    # condition_3 = golden cross

    if condition_1 and condition_2:
        finaldf = finaldf.append({'Ticker': tickers[i], 'PercentReturn': percentreturn, 'Consistency Rating': consistency, 'Current Price': current_price}, ignore_index=True)

print(finaldf)
    #if simple_moving_average(i):
        #print(i + " is consistent")
    #else:
        #print(i + " is not consistent")
