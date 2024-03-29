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
import time

import backtrader.indicators as btind

class Hodl(bt.Strategy):
    def __init__(self):
        pass

    def next(self):
        stake = 1 / len(self.datas)
        #for d in self.datas:
        self.order_target_percent(target=stake, data=self.datas[0])

class SMA_CrossOver(bt.Strategy):
    params = (
        ('fast', 10),
        ('slow', 30),
        ('_movav', btind.MovAv.SMA)
    )

    def __init__(self):
        sma_fast = self.p._movav(period=self.p.fast)
        sma_slow = self.p._movav(period=self.p.slow)
        self.buysig = btind.CrossOver(sma_fast, sma_slow)

    def next(self):
        stake = 1 / len(self.datas)
        if self.buysig > 0:
            self.order_target_percent(target=stake, data=self.datas[0])

        elif self.buysig < 0:
            self.order_target_percent(target=0.0, data=self.datas[0])

# Create a Stratey
class MyStrategy(bt.Strategy):
    params = (
        ('ssa_window', 15),
        ('maperiod', 15),
    )
 
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
 
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
 
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
 
        # Add a MovingAverageSimple indicator
        # self.ssa = ssa_index_ind(
        #     self.datas[0], ssa_window=self.params.ssa_window)
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)
 
 
    def next(self):
        if self.order:
            return
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.order = self.buy()
 
        else:
 
            if self.dataclose[0] < self.sma[0]:
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
 
    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()))


class firstStrategy(bt.Strategy):
    params = (
        ('maxlevel', 70),
        ('minlevel', 20),
    )
    
    def __init__(self):
        self.lastbuy = 0
        self.revenue = 0
        self.totalrevenue = 0
        self.tradetime = 0
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)
        self.dataclose = self.datas[0].close
        self.kd = bt.indicators.StochasticSlow(self.datas[0], period = 9, period_dfast= 3, period_dslow = 3)
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def next(self):
        if not self.position:
            if self.kd[-1] > self.params.minlevel and self.kd[0] < self.params.minlevel:
                self.lastbuy = self.dataclose[0]
#                print('Buy, %.2f' % self.dataclose[0])
                self.buy(size=100)
        else:
            if self.kd[-1] < self.params.maxlevel and self.kd[0] > self.params.maxlevel:
                self.tradetime = self.tradetime + 1
                self.revenue = self.dataclose[0] - self.lastbuy
                self.totalrevenue = self.totalrevenue + self.revenue
#                print('Sell, %.2f' % self.dataclose[0])
#                print('Trade times ${}'.format(self.tradetime), 'Revenue ${}'.format(self.revenue), 'Total revenue ${}'.format(self.totalrevenue))
                self.revenue = 0
                self.lastbuy = 0
                self.sell(size=100)
        
#        if not self.position:
#            if self.rsi < 30:
#                print('Buy, %.2f' % self.dataclose[0])
#                self.buy(size=100)
#        else:
#            if self.rsi > 50:
#                print('Sell, %.2f' % self.dataclose[0])
#                self.sell(size=100) 

#    def notify_order(self, order):
#        if order.status in [order.Submitted, order.Accepted]:
#            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
#            return
#
#        # Check if an order has been completed
#        # Attention: broker could reject order if not enough cash
#        if order.status in [order.Completed]:
#            if order.isbuy():
#                self.log(
#                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
#                    (order.executed.price,
#                     order.executed.value,
#                     order.executed.comm))
#
#                self.buyprice = order.executed.price
#                self.buycomm = order.executed.comm
#            else:  # Sell
#                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
#                         (order.executed.price,
#                          order.executed.value,
#                          order.executed.comm))
#
#            self.bar_executed = len(self)
#
#        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
#            self.log('Order Canceled/Margin/Rejected')
#
#        # Write down: no pending order
#        self.order = None
#    def notify_trade(self, trade):
#        if not trade.isclosed:
#            return
#        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
#                 (trade.pnl, trade.pnlcomm))
    def stop(self):
        self.log('(minlevel %2d) (maxlevel %2d) Ending Value %.2f' %
                 (self.params.minlevel, self.params.maxlevel, self.broker.getvalue()))
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
    bt_df['date'].replace(regex=['101'], value='2012', inplace=True)
    bt_df['date'].replace(regex=['102'], value='2013', inplace=True)
    bt_df['date'].replace(regex=['103'], value='2014', inplace=True)
    bt_df['date'].replace(regex=['104'], value='2015', inplace=True)
    bt_df['date'].replace(regex=['105'], value='2016', inplace=True)
    bt_df['date'].replace(regex=['106'], value='2017', inplace=True)
    bt_df['date'].replace(regex=['107'], value='2018', inplace=True)
    bt_df[["open", "high","low", "close", "volume"]] = bt_df[["open", "high","low", "close", "volume"]].apply(pd.to_numeric)
    bt_df["date"] = bt_df["date"].apply(pd.to_datetime)
    print(bt_df)
    bt_df.to_csv('example.txt', index=False)

#    print(bt_df)

def main():
    
#    tw2bt()

    #Variable for our starting cash
    startcash = 10000
    
    #Create an instance of cerebro
    cerebro = bt.Cerebro()
    
    #Add our strategy
#    cerebro.addstrategy(firstStrategy)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(SMA_CrossOver)
    cerebro.addstrategy(Hodl)
#    cerebro.optstrategy(
#        MyStrategy,
#        maperiod=range(10, 31))

#    cerebro.optstrategy(
#        firstStrategy,
#        minlevel=range(5, 40),
#        maxlevel=range(60, 100),
#        )
    
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
#    dataframe = dataframe.head(200)
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
    
#    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
#    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name = 'SharpeRatio')
#    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')

    # Run over everything
    results = cerebro.run()
    
#    start = results[0]
#    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
#    print('SR:', start.analyzers.SharpeRatio.get_analysis())
#    print('DW:', start.analyzers.DW.get_analysis())

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