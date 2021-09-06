from flask import Flask, render_template, jsonify
import requests
import pickle
import numpy as np
import json
import pandas as pd
from datetime import datetime
import xgboost as xgb
from xgboost import Booster
booster = Booster()
import gzip

print(xgb.__version__)

app = Flask(__name__)

df_all = pd.DataFrame()

class obj:
      
    # constructor
    def __init__(self, dict1):
        self.__dict__.update(dict1)
   
def dict2obj(dict1):
      
    # using json.loads method and passing json.dumps
    # method and custom object hook as arguments
    return json.loads(json.dumps(dict1), object_hook=obj)

def get_tmpid_pred(row):
    if row['tmp'] < 285 :
        return 1
    return 2

def get_d1_day(dayofweek):
  if dayofweek==5 : return 2
  elif dayofweek==6 : return 3
  else : return 1
  
def get_d2_day(dayofweek):
  if dayofweek==0 : return 1
  elif dayofweek==5 : return 3
  elif dayofweek==6 : return 4
  else : return 2



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict_api', methods=['GET'])
def predict_api():

    url = 'https://api.weather.gov/gridpoints/PBZ/77,65/forecast/hourly'

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    res = dict2obj(json.loads(requests.get(url, headers=headers).content))
    print('Calling API')
    tmp_forecast = json.loads(requests.get(url, headers=headers).content)['properties']['periods']
    tmp_forecast = pd.DataFrame.from_dict(tmp_forecast)
    x_forecast = pd.DataFrame()
    x_forecast['datetime'] = tmp_forecast['startTime']
    x_forecast['tmp'] = 273.5 + ((tmp_forecast['temperature'] - 32.0) * (5.0/9.0))

    x_forecast['datetime'] = pd.to_datetime(x_forecast['datetime'], errors='coerce', utc=True).dt.tz_localize(None)
    # x_forecast['datetime'] = x_forecast.apply(lambda row: datetime.strptime(row.datetime, '%Y-%m-%dT%H:%M:%S%z'), axis=1)
    # x_forecast['datetime'] = x_forecast['datetime']
    # x_forecast
    x_forecast['hour'] = x_forecast['datetime'].dt.hour
    x_forecast['month'] = x_forecast['datetime'].dt.month
    x_forecast['tmpid'] =  x_forecast.apply(lambda row: get_tmpid_pred(row), axis=1)
    # x_forecast['tmp2'] = x_forecast.tmp*x_forecast.tmp
    x_forecast['d1'] = x_forecast.apply(lambda row: get_d1_day(row.datetime.day), axis=1)
    x_forecast['d2'] = x_forecast.apply(lambda row: get_d2_day(row.datetime.day), axis=1)
    x_forecast['tmp_tmpid'] = x_forecast.tmp*x_forecast.tmpid
    # # data['tmp2_tmpid'] = data.apply(lambda row: row['tmp2']*row['tmpid'], axis=1)
    x_forecast['tmp_tmpid_month'] = x_forecast.tmp*x_forecast.tmpid*x_forecast.month
    # # data['tmp2_tmpid_month'] = data.tmp2*data.tmpid*data.month
    x_forecast['tmp_tmpid_hour'] = x_forecast.tmp*x_forecast.tmpid*x_forecast.hour
    x_forecast['tmp2_tmpid_hour'] = x_forecast.tmp*x_forecast.tmp*x_forecast.tmpid*x_forecast.hour
    x_forecast['dtmp_tmpid_hour'] = x_forecast.tmp.diff()*x_forecast.tmpid*x_forecast.hour

    x_forecast.dropna(inplace=True)

    x_forecast = x_forecast[['month', 'hour', 'tmp', 'tmpid', 'd1', 'd2', 'tmp_tmpid',
        'tmp_tmpid_month', 'tmp_tmpid_hour', 'tmp2_tmpid_hour',
        'dtmp_tmpid_hour', 'datetime']]

    reg = None
    with gzip.open('./energy', 'rb') as ifp:
        reg = pickle.load(ifp)
    
    x_forecast['prediction'] = reg.predict(x_forecast.drop(['datetime'], axis=1))
    output = {}
    output['preds'] = x_forecast[['datetime', 'prediction']].to_numpy().tolist()
    output = jsonify(output)

    # aaa = pd.concat([df_all, x_forecast], sort=False)

    # _ = aaa.plot(x='datetime', y=['label', 'prediction'], figsize=(15, 5))

    # output=aaa


    # prediction = [
    #     [1,2,3],
    #     [4,5,6]
    # ]

    # output = prediction

    return output

if __name__ == '__main__':
    app.run(debug=True);

