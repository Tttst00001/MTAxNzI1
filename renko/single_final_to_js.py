#! python3
import tushare as ts
import numpy as np
import pandas as pd
import time
import talib
import math
import pymongo
import json
ts.set_token('c2284318d101be62a7d4c8d7a69cc67f14af57b58c1c3423f04c28cb')
# code = 'HC2205.SHF'
code = '002558.SZ'

localtime = time.localtime(time.time())
endTime = time.strftime("%Y%m%d", time.localtime())

client = pymongo.MongoClient(host = '127.0.0.1', port = 27017)
FROE = client['renko'][code]


# DCE 大连
# SHF 上海
# ZCE 郑州

pro = ts.pro_api('c2284318d101be62a7d4c8d7a69cc67f14af57b58c1c3423f04c28cb')
# df = pro.fut_daily(ts_code=code, end_date=endTime) # fut
df = ts.pro_bar(ts_code=code, adj="qfq")
df = df.sort_values(by='trade_date')
df = df.reset_index(drop=True)
# print(df)
# ATR 值
_atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=6)
_atrNum =  "%.2f" % _atr[len(_atr)-1] # 取最后值小数后两位
_atrNum = float(_atrNum) # 转浮点

# _atrNum = 109.14

trade_date = df['trade_date']
close = df['close']
vol = df['vol']
basic_close = close[0] # 初始第一格收盘价

cell_open = basic_close # 上升趋势格值开盘价
cell_close = basic_close + _atrNum # 上升趋势格值收盘价

up_num = 0 # 上涨次数
low_num = 0 # 下跌次数
state = '上涨趋势'
num = 0
colorArr = []

SumVol = 0

final_list = [] # 转JS图形
# print(json.loads(df.T.to_json()).values())
for item in range(len(df)):
  if close[item] >= cell_open and close[item] <= cell_close:
    # 价格在上涨范围内
    # print('@', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
    SumVol += vol[item]
    continue
  if close[item] <= cell_open and close[item] >= cell_close:
    # 价格在下跌范围内
    SumVol += vol[item]
    continue

  if close[item] - cell_close > 0:
    # 上涨
    if state == '下跌趋势':
      if close[item] - cell_close > 0 and close[item] - cell_close < _atrNum * 2:
        cell_close = cell_open + _atrNum
        state = '上涨趋势'
        up_num += 1
        low_num = 0
        SumVol += vol[item]
        obj = {
          "up_num": up_num,
          "flag": "E",
          "direction": "上涨一格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(up_num, 'E 上涨一格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
      elif close[item] - cell_close > _atrNum * 2:
        cell_open = cell_open + _atrNum * math.floor((close[item] - cell_open) / _atrNum)
        cell_close = cell_open + _atrNum
        state = '上涨趋势'
        SumVol += vol[item]
        up_num += 1
        low_num = 0
        obj = {
          "up_num": up_num,
          "flag": "F",
          "direction": "上涨多格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(up_num, 'F 上涨多格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
    else:
      if close[item] - cell_close > 0 and close[item] - cell_close < _atrNum * 2:
        cell_open = cell_close
        cell_close = cell_open + _atrNum
        state = '上涨趋势'
        SumVol += vol[item]
        up_num += 1
        low_num = 0
        obj = {
          "up_num": up_num,
          "flag": "G",
          "direction": "上涨一格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(up_num, 'G 上涨一格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
      elif close[item] - cell_close > _atrNum * 2:
        cell_open = cell_open + _atrNum * math.floor((close[item] - cell_open) / _atrNum)
        cell_close = cell_open + _atrNum
        state = '上涨趋势'
        SumVol += vol[item]
        up_num += 1
        low_num = 0
        obj = {
          "up_num": up_num,
          "flag": "H",
          "direction": "上涨多格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(up_num, 'H 上涨多格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
      elif close[item] - cell_close < 0 and close[item] - cell_close > -_atrNum * 2:
        # 下跌一格
        cell_close = cell_open - _atrNum
        state = '下跌趋势'
        SumVol += vol[item]
        up_num = 0 
        low_num += 1
        obj = {
          "up_num": up_num,
          "flag": "I",
          "direction": "下跌一格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(low_num, 'I 下跌一格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
      elif close[item] - cell_close < -_atrNum * 2:
        # 下跌多格
        cell_open = cell_open - _atrNum * math.floor((cell_open - close[item]) / _atrNum)
        cell_close = cell_open - _atrNum
        state = '下跌趋势'
        SumVol += vol[item]
        up_num = 0 
        low_num += 1
        obj = {
          "up_num": up_num,
          "flag": "J",
          "direction": "下跌多格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(low_num, 'J 下跌多格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
  else:
    # 下跌
    # 下跌趋势  下跌一格 & 下跌多格
    if state == '下跌趋势': 
      if close[item] - cell_close >= -_atrNum and close[item] - cell_close <= 0:
        cell_open = cell_close
        cell_close = cell_open - _atrNum
        SumVol += vol[item]
        up_num = 0 
        low_num += 1
        obj = {
          "up_num": up_num,
          "flag": "A",
          "direction": "下跌一格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(low_num, 'A 下跌一格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
      elif close[item] - cell_close < _atrNum:
        cell_open = cell_open - _atrNum * math.floor((cell_open - close[item]) / _atrNum)
        cell_close = cell_open - _atrNum
        SumVol += vol[item]
        up_num = 0 
        low_num += 1
        obj = {
          "up_num": up_num,
          "flag": "B",
          "direction": "下跌多格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(low_num, 'B 下跌多格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)

    if state == '上涨趋势':
      if close[item] - cell_close < 0 and close[item] - cell_close > -_atrNum * 2:
        # 下跌一格
        cell_close = cell_open - _atrNum
        SumVol += vol[item]
        up_num = 0 
        low_num += 1
        obj = {
          "up_num": up_num,
          "flag": "C",
          "direction": "下跌一格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(low_num, 'C 下跌一格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
      elif close[item] - cell_close < -_atrNum * 2:
        cell_open = cell_open - _atrNum * math.floor((cell_open - close[item]) / _atrNum)
        cell_close = cell_open - _atrNum
        SumVol += vol[item]
        up_num = 0 
        low_num += 1
        obj = {
          "up_num": up_num,
          "flag": "D",
          "direction": "下跌多格",
          "date": trade_date[item],
          "close": close[item],
          "cell_open": cell_open,
          "cell_close": cell_close,
          "vol": SumVol
        }
        final_list.append(obj)
        SumVol = 0
        print(low_num, 'D 下跌多格', trade_date[item], 'close', close[item], 'cell_open', cell_open, 'cell_close', cell_close)
    state = '下跌趋势'
    # 下跌趋势 没有上涨
print('ATR:', _atrNum, 'up_num', up_num, 'low_num', low_num)

for item in final_list:
    # print(item)
    FROE.insert_one(item)