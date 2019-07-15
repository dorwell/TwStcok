#
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 18:27:56 2019

@author: wade.lin
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests as rq
import matplotlib.pyplot as plt
import talib as ta
import time
# Get a dataframe from twse
# date: 20110401
# date: 0050

#class Order():
#    def __init__(self):
#        self.

def backtesting_v1(dataframe):
    buy_price = 0 
    earning = 0
    trade_count = 0
    for index, row in dataframe.iterrows():
#        if(row['end_5day'].isnull()):
#            continue
        if(float(row['end_2day'])>float(row['end_5day'])):
            if(buy_price == 0):
                print("Buy", index, row['date'], row['end'],row['end_5day'])
                buy_price = float(row['end'])
        if(float(row['end_2day'])<float(row['end_5day'])):
            if(buy_price > 0):
                print("Sell", index, row['date'], row['end'],row['end_5day'])
                diff =(buy_price - float(row['end']))
                earning = earning + diff
                print("\t Earning:"+str(diff))
                buy_price = 0
                trade_count += 1
    print("Trade count:"+str(trade_count))            
    print("Total earning:"+str(earning))            
    
def twstock_mon(date,stocknum):
    # Check parameters
    url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=html&date="+date+"&stockNo="+stocknum
    rows_list = list()
    response = rq.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find_all('tr')
    idx = 0
    for tr in trs:
#        print(tr)
#        print('##################')
        if(idx >= 2):
            cols = tr.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            rows_list.append(cols)
        idx+=1
#        rows_list.append([td.text.replace('\n', '').replace('\xa0', '') for td in tr.find_all('td')])
    labels =['date', 'trans', 'exchange', 'begin', 'highest', 'lowest', 'end', 'difference', 'volume']
    df = pd.DataFrame.from_records(rows_list, columns = labels)
    return df

def parse_stock():
    stocknum = "0050"
    dfs = []
    for year in range(2011, 2019, 1):
        for month in range(1, 13, 1):
    #        df = twstock_mon(,stocknutwm)
#           print(str(year).zfill(2), str(month).zfill(2))
            str_date = "{:04d}".format(year)+"{:02d}".format(month)+"01"
            print("Parse "+str_date)
            dfs.append(twstock_mon(str_date, stocknum))
            time.sleep(6)
#    df1 = twstock_mon(date,stocknum)
#    df2 = twstock_mon("20110501",stocknum)
#    dfs = [df1, df2]
#    print(type(dfs))
    res_df = pd.concat(dfs,axis=0, ignore_index=True)
    res_df.to_pickle('res_df.pkl')    

def DF_TW2BT(df_tw):
    bt_df = df_tw.loc[:,['date', 'begin', 'highest', 'lowest', 'end', 'volume']]
#    print(bt_df)
    bt_df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    bt_df['openinterest'] = 0
    bt_df['date'].replace('-','/', inplace=True)
    bt_df.replace({'date': '2006-'}, {'date': '100-'}, regex=True)
    print(bt_df)
    rtn_df = bt_df.replace(regex=['/'], value='-')
    rtn_df = rtn_df.replace(regex=[','], value='')
    rtn_df = rtn_df.iloc[1:60,:]
    rtn_df.to_pickle('bt_df.pkl')
    
    return rtn_df

def main():
    
#    parse_stock()
#    return 
    win_2 = 5
    win_3 = 20
    res_df = pd.read_pickle('res_df.pkl')
    #res_df = pd.DataFrame(res_df)
#    print(res_df)
    
    DF_TW2BT(res_df)
    return
    
    #print(res_df.iloc[:,1:2])
    col_end = res_df.iloc[:,6:7]
    #print(col_end)
    col_end_avg_1day = col_end.rolling(window=1).mean()
    col_end_avg_2day = col_end.rolling(window=win_2).mean()
    col_end_avg_5day = col_end.rolling(window=win_3).mean()
    #col_end_avg_5day.columns = ['end_5day']
    col_end_avg_2day.rename(columns={'end':'end_2day'}, inplace=True)
    col_end_avg_5day.rename(columns={'end':'end_5day'}, inplace=True)
#    print(col_end_avg_2day)
#    print(col_end_avg_5day)
    #print(type(col_end))
    #print(type(col_end_avg_2day))
    ## Append by column
    df_append_col = pd.concat([res_df,col_end_avg_2day], axis=1)
    df_append_col = pd.concat([df_append_col,col_end_avg_5day], axis=1)
#    print(df_append_col)
#    for index, row in df_append_col.iterrows():
#        row['end_5day'] = 0
#        print(index, row['date'], row['end'])
    #assign a value to a specific cell
    #df_append_col['end_5day'][1] = 0
    df_append_col.drop([0,win_3])
#    print(df_append_col)
    backtesting_v1(df_append_col)
    #result = pd.DataFrame({'end':col_end, 'AVG 2 Day':col_end_avg_2day, 'AVG 5 Day': col_end_avg_5day})
    #result.plot()
    col_end_MA = ta.MA(res_df.end)
    ax = col_end_avg_2day.plot(kind='line')
#    ax = col_end_avg_5day.plot(ax = ax)
#    ax = col_end_avg_1day.plot(ax = ax)
    ax = col_end_MA.plot(ax = ax)
    #col_end_avg_5day.plot(kind='line',x='name',y='num_children')
    plt.show()
    
    
    #for tr in trs:
    #    print(tr)
    #    print('#################')
    #    tds = soup.find_all('td')
    #    for td in tds:
    #        print(td.string)        
            
    
    #
    #dfs = pd.read_html(url)[0]
    #dfs2 = pd.read_html(url2)[0]
    ##print(dfs)
    #
    #for index, row in dfs:
    #    print(dfs[index])
    #    print(str(index)+","+str(row))
    ##    print(dfs[row])
    ##print(dfs[b''])
    #
    ##print(dfs.loc[:,:])
    #    
    #
    #df1 = dfs.ix[:,0:2]
    ##print(df1)
    #print("#############################")
    #      
    #df2 = dfs2.ix[:,0:2]
    ##print(df2)
    #print("#############################")
    #res = pd.concat([df1, df2], axis=0)
    ##print(res)
    #print(type(dfs))
    #print(type(df1))
    #print(type(url))
    #print(type(dfs[index]))

if __name__ == '__main__':
    main()
