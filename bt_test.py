# -*- coding: utf-8 -*-
"""
Created on Mon Jul 8 16:04:40 2019

@author: wade.lin
"""
import pandas as pd
import backtrader as bt
from datetime import datetime

class firstStrategy(bt.Strategy):

def __init__(self):
    self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)
    
    def next(self):
    if not self.position:
    if self.rsi < 40:
    self.buy(size=100)
    else:
    if self.rsi > 50:
    self.sell(size=100)



#bt_df = pd.read_pickle('bt_df.pkl')
#bt_df.to_csv('example.txt', index=False)
#bt_df[["open", "high","low", "close", "volume"]] = bt_df[["open", "high","low", "close", "volume"]].apply(pd.to_numeric)
#bt_df["date"] = bt_df["date"].apply(pd.to_datetime)
#print(bt_df)


#Variable for our starting cash
startcash = 10000

#Create an instance of cerebro
cerebro = bt.Cerebro()

#Add our strategy
cerebro.addstrategy(firstStrategy)

#Get Apple data from Yahoo Finance.
#data = bt.feeds.Quandl(
# dataname='AAPL',
# fromdate = datetime(2016,1,1),
# todate = datetime(2017,1,1),
# buffered= True
# )
#print(data)
#
#print(type(data))
#data = bt.feeds.PandasData(dataname=bt_df)

datapath = ('example.txt')

# Simulate the header row isn't there if noheaders requested
#skiprows = 1 if args.noheaders else 0
#header = None if args.noheaders else 0

dataframe = pd.read_csv(
datapath,
# skiprows=skiprows,
# header=header,
# parse_dates=[0],
parse_dates=True,
index_col=0,
)

print(dataframe)
dataframe['date'].replace('100-','2006-', inplace=True)

# Pass it to the backtrader datafeed and add it to the cerebro
data = bt.feeds.PandasData(dataname=dataframe,
# datetime='Date',
nocase=True,
)


#data0 = bt.feeds.PandasData(dataname=bt_df, fromdate = datetime.datetime(100, 1, 4), todate = datetime.datetime(100, 4, 7))
cerebro.adddata(data)

#Add the data to Cerebro
#cerebro.adddata(data)

# Set our desired cash start
cerebro.broker.setcash(startcash)

# Run over everything
cerebro.run()

#Get final portfolio Value
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

#Print out the final result
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

#Finally plot the end results
cerebro.plot(style='candlestick')