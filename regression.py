import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from sklearn import preprocessing
import seaborn as sns
import xgboost as xgb
from xgboost import plot_importance, plot_tree
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime as dt
plt.style.use('fivethirtyeight')

pjme_df = pd.read_csv('./data/PJME_hourly.csv')
pjme_df.columns = ['datetime', 'load']

temp_df = pd.read_csv('./data/temperature.csv')[['datetime', 'Pittsburgh']]
temp_df.columns = ['datetime', 'temperature']

df = pd.merge(pjme_df, temp_df, how='inner', on = 'datetime')

df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

df['hour'] = df['datetime'].dt.hour
df['dayofweek'] = df['datetime'].dt.dayofweek
df['dayofmonth'] = df['datetime'].dt.day
df['month'] = df['datetime'].dt.month
df.dropna()

plt.figure(figsize=(15, 10))
plt.scatter(df.datetime, df.load, s=1)
plt.xlabel('Time of the Year')
plt.ylabel('Load')
plt.title('How consumption varies throught the year')
plt.savefig('./images/how-consumption-varies-throught-the-year.png')

plt.figure(figsize=(15, 10))
plt.scatter(df.temperature, df.load, s=1)
plt.xlabel('Temperature')
plt.ylabel('Load')
plt.title('How consumption varies with temperature')
plt.savefig('./images/how-consumption-varies-with-temperature.png')

plt.figure(figsize=(15, 10))
plt.scatter(df.datetime, df.temperature, s=5)
plt.xlabel('hours of the year')
plt.ylabel('Temperature')
plt.title('How temperature varies throught the year')
plt.savefig('./images/how-temperature-varies-throught-the-year.png')

plt.figure(figsize=(40, 20))
plt.tight_layout()
plt.rcParams.update({'font.size': 16})
for m in range(1, 13):
    t = df[df['month']==m]
    plt.subplot(3, 4, m)
    plt.scatter(t[['temperature']], t[['load']], s=20)
    plt.xlabel('Temperature')
    plt.ylabel('Load')
    plt.title('Load for month ' + str(m))
plt.savefig('./images/load-temperature-month-plots.png')

plt.figure(figsize=(30,60))
plt.tight_layout()
plt.rcParams.update({'font.size': 12})
for hr in range(1, 24):
    t = df[df['hour']==hr]
    plt.subplot(8, 3, hr)
    plt.scatter(t[['temperature']], t[['load']], s=20)
    plt.xlabel('Temperature')
    plt.ylabel('Load')
    plt.title('Load for hour ' + str(hr))
plt.savefig('./images/load-temperature-hour-plots.png')

def get_tmpid(row):
    if row['temperature'] < 285 :
        return 1
    return 2

def get_d1(row):
  if row['dayofweek']==5 : return 2
  elif row['dayofweek']==6 : return 3
  else : return 1

  
def get_d2(row):
  if row['dayofweek']==0 : return 1
  elif row['dayofweek']==5 : return 3
  elif row['dayofweek']==6 : return 4
  else : return 2

data = pd.DataFrame()
data['month'] = df['month']
data['hour'] = df['hour']
data['tmp'] = df['temperature']
data['tmp2'] = df.temperature*df.temperature
data['tmpid'] = df.apply(lambda row: get_tmpid(row), axis=1)
data['d1'] = df.apply(lambda row: get_d1(row), axis=1)
data['d2'] = df.apply(lambda row: get_d2(row), axis=1)
data['tmp_tmpid'] = data.apply(lambda row: row['tmp']*row['tmpid'], axis=1)
# data['tmp2_tmpid'] = data.apply(lambda row: row['tmp2']*row['tmpid'], axis=1)
data['tmp_tmpid_month'] = data.tmp*data.tmpid*data.month
# data['tmp2_tmpid_month'] = data.tmp2*data.tmpid*data.month
data['tmp_tmpid_hour'] = data.tmp*data.tmpid*data.hour
data['tmp2_tmpid_hour'] = data.tmp2*data.tmpid*data.hour
data['dtmp_tmpid_hour'] = data.tmp.diff()*data.tmpid*data.hour
data['label'] = df['load']
data['datetime'] = df['datetime']
data.drop(['tmp2'], inplace=True, axis=1)
data.dropna(inplace=True)

split_date = '01-Jan-2017'
df_train = data.loc[data.datetime < split_date].copy()
df_test = data.loc[data.datetime >= split_date].copy()
# df_train.drop(['datetime'], axis=1, inplace=True)
# df_test.drop(['datetime'], axis=1, inplace=True)

# df_train=(df_train-df_train.mean())/df_train.std()
# df_test=(df_test-df_test.mean())/df_test.std()


x_train = df_train.drop(['label'], axis=1)
x_test = df_test.drop(['label'], axis=1)
y_train = df_train.label
y_test = df_test.label
x_train = x_train.reset_index().drop(['index'], axis=1)
x_test = x_test.reset_index().drop(['index'], axis=1)
y_train = y_train.reset_index().drop(['index'], axis=1)
y_test = y_test.reset_index().drop(['index'], axis=1)

# ml = LinearRegression()
# ml.fit(x_train, y_train)
# y_pred = ml.predict(x_test)

# r2 = r2_score(y_test, y_pred)
# adj_r2 = 1 - (1 - r2)*((len(data)-1)/(len(data)-data.shape[1]-1))
# adj_r2

reg = xgb.XGBRegressor(n_estimators=1000)
reg.fit(x_train.drop(['datetime'], axis=1), y_train,
        eval_set=[(x_train.drop(['datetime'], axis=1), y_train), (x_test.drop(['datetime'], axis=1), y_test)],
        early_stopping_rounds=50,
       verbose=False)

reg.predict(x_test[:1].drop(['datetime'], axis=1))

import pickle, gzip

pick_insert = open('./model/energy','wb')
with gzip.open(pick_insert, 'wb') as ofp:
    pickle.dump(reg, ofp)
pick_insert.close()

_ = plot_importance(reg, height=0.9)

_.figure.savefig('./images/variable-importance-plot.png')

df_test['prediction'] = reg.predict(x_test.drop(['datetime'], axis=1))
df_all = pd.concat([df_train, df_test], sort=False)

_ = df_all.plot(x='datetime', y=['label', 'prediction'], figsize=(15, 5))

_.figure.savefig('./images/prediction-2017-plot.png')

mean_absolute_error(y_true=df_test['label'],
                   y_pred=df_test['prediction'])

mean_absolute_error(y_true=df_test['label'],
                   y_pred=df_test['prediction'])

def mean_absolute_percentage_error(y_true, y_pred): 
    """Calculates MAPE given y_true and y_pred"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

mean_absolute_percentage_error(y_true=df_test['label'],
                   y_pred=df_test['prediction'])


import requests
import json

def get_d1_day(dayofweek):
  if dayofweek==5 : return 2
  elif dayofweek==6 : return 3
  else : return 1
  
def get_d2_day(dayofweek):
  if dayofweek==0 : return 1
  elif dayofweek==5 : return 3
  elif dayofweek==6 : return 4
  else : return 2

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

url = 'https://api.weather.gov/gridpoints/PBZ/77,65/forecast/hourly'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
res = dict2obj(json.loads(requests.get(url, headers=headers).content))

tmp_forecast = json.loads(requests.get(url, headers=headers).content)['properties']['periods']
tmp_forecast = pd.DataFrame.from_dict(tmp_forecast)
x_forecast = pd.DataFrame()
x_forecast['datetime'] = tmp_forecast['startTime']
x_forecast['tmp'] = 273.5 + ((tmp_forecast['temperature'] - 32.0) * (5.0/9.0))

# month	hour	tmp	tmpid	d1	d2	tmp_tmpid	tmp_tmpid_month	tmp_tmpid_hour	tmp2_tmpid_hour	dtmp_tmpid_hour	datetime

from datetime import datetime
# 2021-09-06T01:00:00-04:00

x_forecast['datetime'] = pd.to_datetime(x_forecast['datetime'], errors='coerce', utc=True).dt.tz_localize(None)
x_forecast['hour'] = x_forecast['datetime'].dt.hour
x_forecast['month'] = x_forecast['datetime'].dt.month
x_forecast['tmpid'] =  data.apply(lambda row: get_tmpid_pred(row), axis=1)

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

cols_when_model_builds = reg.get_booster().feature_names
x_forecast = x_forecast[['month', 'hour', 'tmp', 'tmpid', 'd1', 'd2', 'tmp_tmpid',
       'tmp_tmpid_month', 'tmp_tmpid_hour', 'tmp2_tmpid_hour',
       'dtmp_tmpid_hour', 'datetime']]
# x_forecast.columns
x_forecast['prediction'] = reg.predict(x_forecast.drop(['datetime'], axis=1))
aaa = pd.concat([df_all[df_all.datetime > '1-jan-2021'], x_forecast], sort=False)

_ = aaa.plot(x='datetime', y=['label', 'prediction'], figsize=(15, 5))

_.figure.savefig('./images/one-week-plot.png')



