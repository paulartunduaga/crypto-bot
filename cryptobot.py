# -*- coding: utf-8 -*-
"""
Spyder Editor
This is a temporary script file.
"""

import numpy as np
import time

import requests
from urllib.parse import urljoin, urlencode
import time
import pandas as pd
from binance.client import Client



api_key = 'xxxxx'

secret_key = 'xxxxx'

client = Client(api_key, secret_key, {"timeout": None})



#get current for all markets price

def currentprice():
    headers = {'X-MBX-APIKEY': api_key}
    BASE_URL = 'https://api.binance.com'
    PATH = '/api/v3/ticker/price'
    params = {'symbol': None}
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    df = pd.DataFrame(r.json())
    return df

def buy(market):
    order = client.create_order(
        symbol='BTCUSDT',
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=0.002)
    
    time.sleep(10)
    
    while len(client.get_open_orders(symbol='BTCUSDT')) > 0:    #wait till order has gone through
        pass
    
    quantity = float(np.format_float_positional((0.002
                                                 / currentpricepop(market)), precision=4, 
                                                unique=False, fractional=False, trim='.'))
    if quantity > 100:
        quantity = int(quantity)
    
    order = client.create_order(
        symbol = market,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity)
    
    
def sell(market, asset):
    
    quantity=float(np.format_float_positional(float(client.get_asset_balance(asset=asset)['free']), precision=4,
    unique=False, fractional=False, trim='.'))  #get balance of asset being sold 
    
    if quantity > 100:
        quantity = int(quantity)
    
    order = client.create_order(
        symbol=market,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=float(quantity))  #get balance of asset being sold 
    
    time.sleep(5)
    
    while len(client.get_open_orders(symbol=market)) > 0:
              pass
                        
    
    quantity1 = np.format_float_positional(float(client.get_asset_balance(asset='BTC')['free']),
    precision=4, unique=False, fractional=False, trim='.')
    
    print(quantity1)
    
    
    order = client.create_order(
        symbol = 'BTCUSDT',
        side = Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity = float(quantity1)) #get balance of bitcoin to specify
                                     #how much to sell
                                     
                                     
#had to make another almost identical function - but has an index parameter in pd.Dataframe - this is needed cos
#single market being pulled

def currentpricepop(market):
    headers = {'X-MBX-APIKEY': api_key}
    BASE_URL = 'https://api.binance.com'
    PATH = '/api/v3/ticker/price'
    params = {'symbol': market}
    url = urljoin(BASE_URL, PATH)
    r = requests.get(url, headers=headers, params=params)
    df = pd.DataFrame(r.json(), index=[0])
    return float(df.iloc[0,1])                    
    

  
positions_held = 0

while positions_held == 0: 
    
    all_current_prices = currentprice()
    symbols = all_current_prices['symbol'].tolist() #contains list of all symbols

    
    potential_targets = []


    only_BTC_and_over_24 = []   #only bitcoin markets 

    for symbol in symbols:
        if symbol[-3:] == 'BTC' and float(client.get_ticker(symbol=symbol)['priceChangePercent']) > 1:
            only_BTC_and_over_24.append(symbol)
            
    
    
    for symbol in only_BTC_and_over_24:
        klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_15MINUTE, "1 hour ago UTC") #pull data
        mins15 = pd.DataFrame(klines) #to df
        
        for columns in mins15.columns:
            mins15[columns] = pd.to_numeric(mins15[columns])  #to numeric for calculation
    
        mins15 = mins15.rename(columns={0: symbol, 1: 'Open', 2: 'Close'})  #rename frame column to symbol

        potential_targets.append(mins15)
    
    #create list where there has been 15 minute positive movements above 7.5% 

    overlist = []

    for frame in potential_targets:
        if frame.empty:
            continue
    
    #ignores empty dataframes returned from response
        else:
            frame = frame.drop(columns=[3,4,5,6,7,8,9,10,11])
        
        #drop useless columns 
            frame['Change (%)'] = ((frame.iloc[:,2] - frame.iloc[:,1]) / frame.iloc[:,1]) * 100
        
        #calculate our change 
        
            if (frame['Change (%)'] > 3.5).any() and frame.shape == (4,4):      #shape was cos some werent coming in 3x3 
                overlist.append(frame)
            
        #filter as required    
    
      #annoyingly longwinded but.. now keeping only markets where movement in the last 15 minutes has been plus 7.5%

    buy_list = []
    
    for frame in overlist:
        if frame.iloc[3,3] > 2.5 and (frame.iloc[3,2] > 0.75 and frame.iloc[3,1] > 0.75 and frame.iloc[3,0] > 0.75):
            buy_list.append(frame)
        
       #limit to only two markets - as per strategy - by choosing first two items in list
        
    buy_list = buy_list[0:2]
        
        
        
        
        
        # here we extract the BTC market we want to buy into producing 1 or 2 assets to buy - only 1 if there is only one
#market which has moved more than 7.5% in last 15 minutes.

    if len(buy_list) == 1:
        asset1 = buy_list[0].columns.tolist()
        asset1 = asset1[0]
  
            
        buy(asset1)  #buy asset1
    
        trades1 = client.get_my_trades(symbol = asset1)  #record purchase price

        purchaseprice1 =  trades1[0]["price"]   #record purchase price
            
        purchaseprice2 = "No second asset"
    
        historical_price_tenure1 = []   #start historical record
    
        positions_held = 1
    
    if len(buy_list) == 2: 
        asset1 = buy_list[0].columns.tolist() 
        asset1 = asset1[0]
    
        asset2 = buy_list[1].columns.tolist()
        asset2 = asset1[0]
    

                                    
        buy(asset1)  #buy asset1
                                    
        trades1 = client.get_my_trades(symbol = asset1)

        purchaseprice1 =  trades1[0]["price"]   #record purchase price asset1
    
        historical_price_tenure1 = []  #start historical record
                                    
        positions_held += 1
                                    
                                    
                                    
        buy(asset2)    #buy asset2
    
        trades2 = client.get_my_trades(symbol = asset2)
    
        purchaseprice2 = trades2[0]['price']    #record purchase price asset2
    
        historical_price_tenure2 = []   #start historical record
                                    
        positions_held += 1
                                    
                                    
    
    
    else:
        print('Buying conditions not met')
        time.sleep(60)
        pass

    
    
    
              

print('DONE', purchaseprice1, asset1, purchaseprice2)


if positions_held == 2: 
    asset1_sold = 1
    asset2_sold = 1 

else:
    asset1_sold = 1
    asset2_sold = 0

while positions_held > 0:
    
    
    
    
    
    #get BTC 24 change for rule 1
    
    BTC_24 = float(client.get_ticker(symbol='BTCUSDT')['priceChangePercent'])
    
    

    
    if asset1_sold == 1:
        
        
        currentprice1 = float(currentpricepop(asset1))  #current price of asset
         
        historical_price_tenure1.append(float(currentpricepop(asset1)))  #add to historical record
        
        if len(historical_price_tenure1) >= 200:
            highestprice1 = max(historical_price_tenure1[99:])  #get highest price on tenure - highest price
                                                                #only measured after an hour or so IMPORTANT 
                                                                 #otherwise highest price is basicaly just 
                                                                 #the same as purchase price
        
        #pass conditions below - positions held and asset hold value change accordingly
        
        if currentprice1 < 0.93 * float(purchaseprice1) or currentprice1 < 0.98 * highestprice1 or BTC_24 <= -10:
            sell(asset1, asset1.replace('BTC',''))
            asset1_sold -= 1
            positions_held -= 1
        
        else:
            print('holding, current price:', currentprice1,'purchase price:', purchaseprice1)

        
        
        
    if asset2_sold == 1:
            
        currentprice2 = float(currentpricepop(asset2))
        

        historical_price_tenure2.append(float(currentpricepop(asset2)))
        
        if len(historical_price_tenure2) >= 200:
            highest_price2 = max(historical_price_tenure2[99:])
        
        if currentprice2 < 0.93 * purchaseprice2 or currentprice2 < 0.98 * highest_price2 or BTC_24 <= -10:
            sell(asset2, asset2.replace('BTC',''))
            asset2_sold -= 1 
            positions_held -= 1
        
        else:
            print('holding')

            
        
        
        
        
        
        
        
        
    time.sleep(15)
    
    #repeat for asset2
    



print('Trade Completed!')

