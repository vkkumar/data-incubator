# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 00:13:30 2015

@author: vaidyanatk
"""

# Imports
from flask import Flask, render_template, request, redirect
from pandas import DataFrame, to_datetime
from datetime import datetime,timedelta
from bokeh.plotting import figure
from bokeh import embed
import requests
import os

app = Flask(__name__)

selector = {}

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
  return render_template('index.html')

def make_plot():
	types = request.form.getlist('type') 
	
	ticker = request.form['ticker']
	now = datetime.now()
	end_date = now.strftime('%Y-%m-%d') 
	start_date = (now - timedelta(days = 180)).strftime('%Y-%m-%d') # six - month timeframe

	URL = 'https://www.quandl.com/api/v3/datasets/WIKI/'+ticker+'.json?start_date='+start_date+'&end_date='+end_date+'&order=asc&api_key=eFoXAcyvLhyuB3Rsvg6o'
	r = requests.get(URL)
	df_handle = DataFrame(r.json())
 
	df = DataFrame(df_handle.ix['data','dataset'], columns = df_handle.ix['column_names','dataset'])
	df.columns = [x.lower() for x in df.columns]
	df = df.set_index(['date'])
	df.index = to_datetime(df.index)

	p = figure(x_axis_type = "datetime")
 
	if 'open' in types:
	    p.line(df.index, df['open'], color='blue', legend='opening price')
	if 'high' in types:
	    p.line(df.index, df['high'], color='red', legend='highest price')
	if 'close' in types:
	    p.line(df.index, df['close'], color='green', legend='closing price')
	return p
	

@app.route('/chart',methods=['GET','POST'])
def chart():
	plot = make_plot()
	script, div = embed.components(plot)
	return render_template('stock_plot.html', script = script, div = div)
	
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port = port)