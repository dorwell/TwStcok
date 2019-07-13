# -*- coding: utf-8 -*-
"""
Created on Mon Jul 8 16:04:40 2019

@author: wade.lin
"""
import pandas as pd
import backtrader as bt
from datetime import datetime
import locale
from locale import atof

class firstStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)
        self.dataclose = self.datas[0].close
        self.kd = bt.indicators.StochasticSlow(self.datas[0], period = 9, period_dfast= 3, period_dslow = 3)
    def next(self):
        
        if not self.position:
            if self.rsi < 40:
                print('Buy, %.2f' % self.dataclose[0])
                self.buy(size=100)
        else:
            if self.rsi > 60:
                print('Sell, %.2f' % self.dataclose[0])
                self.sell(size=100) 

def tw2bt():
    res_df = pd.read_pickle('res_df.pkl')
#    print(res_df)
    bt_df = res_df.loc[:, ['date', 'begin', 'highest', 'lowest', 'end', 'volume']]
    bt_df['openinterest'] = '0'
    bt_df.columns = ["date","open", "high","low", "close", "volume", "openinterest"]
#    locale.setlocale(locale.LC_NUMERIC, '')
#    bt_df[["open", "high","low", "close", "volume"]] = bt_df[["open", "high","low", "close", "volume"]].applymap(atof)
    bt_df['volume'].replace(regex=[','], value='', inplace=True)
    bt_df['date'].replace(regex=['/'], value='-', inplace=True)
    bt_df['date'].replace(regex=['100'], value='2011', inplace=True)
    bt_df[["open", "high","low", "close", "volume"]] = bt_df[["open", "high","low", "close", "volume"]].apply(pd.to_numeric)
    bt_df["date"] = bt_df["date"].apply(pd.to_datetime)
    print(bt_df)
    bt_df.to_csv('example.txt', index=False)

#    print(bt_df)

def main():
    
#    tw2bt()

    #Variable for our starting cash
    startcash = 1000000
    
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
    dataframe = dataframe.head(100)
    print(dataframe)
    
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

if __name__ == '__main__':
    main()