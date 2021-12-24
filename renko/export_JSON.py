#! python3
import tushare as ts
import pandas as pd
import numpy as np
import pymongo
import json
from bson import json_util

client = pymongo.MongoClient(host = '127.0.0.1', port = 27017)
# FROE = client['tushare']['2021_08_cci']
FROE = client['renko']['002558.SZ']



with open("collection.json", "w") as f1:
  f1.seek(0)
  f1.truncate()
  print("清空数据")


file = open("collection.json", "w")
file.write('var data = [')
for document in FROE.find():
  # print(document)
  file.write(json_util.dumps(document))
  file.write(',')
file.write(']')