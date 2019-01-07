import numpy as np
import pandas as pd
import quandl
from datetime import datetime
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)

class TickerForm(FlaskForm):
    ticker = StringField('Please type in a valid stock ticker:', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TickerForm()
    if form.validate_on_submit():
        stock = form.ticker.data
        quandl.ApiConfig.api_key = "-1B6MPSvhgmkw-7uLx_x"
        df = quandl.get_table('WIKI/PRICES', ticker=stock, paginate=True)

        # if the ticker is mispelled or there is no data of this stock in the database
        if df.size == 0:
            return render_template('nodata.html', current_time=datetime.utcnow())

        df = df[::-1]
        inc = df.close > df.open
        dec = df.open > df.close
        w = 12*60*60*1000 # half day in ms
        
        # make a plot with 50-day and 200-day moving average
        TOOLS = "pan, wheel_zoom, box_zoom, reset, save"
        p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title = "Data provided by Quandl")
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Price'
        ma50 = df.adj_close.rolling(50).mean()
        ma200 = df.adj_close.rolling(200).mean()
        p.segment(df.date, df.adj_high, df.date, df.adj_low, color='black')
        p.line(df.date, ma50, color='blue', legend='50-Day Moving Average')
        p.line(df.date, ma200, color='red', legend='200-Day Moving Average')
        p.vbar(df.date[inc], w, df.adj_open[inc], df.adj_close[inc], fill_color="#D5E1DD", line_color="black")
        p.vbar(df.date[dec], w, df.adj_open[dec], df.adj_close[dec], fill_color="#F2583E", line_color="black")
        p.legend.location = "top_left"
        script1, div1 = components(p)

        return render_template('stock.html', div1=div1, script1=script1, current_time=datetime.utcnow())
    return render_template('index.html', form=form, current_time=datetime.utcnow())
