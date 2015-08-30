'''
This script is loosely based on the bokeh/examples/embed/simple/simple.py.

'''
#%%
import numpy as np
import requests as rq
import simplejson as sjson
import pandas as pd

import flask
from flask import request, session
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.util.string import encode_utf8

app = flask.Flask(__name__)
app.secret_key = '\x87\x1e2\x89\x0f|"\xf9\xbbh\xabj\xd1\xf8\xaf\xc0\x06\xcd\x9e\xdb\xe5\xc6\xaf\xac'

colors = ['#FF0000','#00FF00','#0000FF']


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

Message = 'Most likely, the ticker you entered was not found in the dataset.'

@app.route("/",methods=["GET","POST"])
def lookup():
    if request.method == 'GET':
        return flask.render_template('welcome.html')
    elif request.method =='POST':
        # a = flask.request.form.get('Volume')

        args = flask.request.form

        if not args['company']:
            flask.flash(Message)
            return flask.redirect(flask.url_for('index'))
            # return flask.render_template('welcome.html')
        else:
            company = args['company']

        session['company'] = args
        return flask.redirect('result')

@app.route('/result')
def result():
    args = session['company']
    r = rq.get('https://www.quandl.com/api/v1/datasets/WIKI/' + args['company'] + '.json')

    if not r.status_code == 200:
        flask.flash(Message)
        return flask.redirect(flask.url_for('index'))
        # return flask.render_template('welcome.html')

    company = args['company']
    data = r.json()
    price = pd.DataFrame(data['data'])
    price.columns = data['column_names']

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    r = figure(x_axis_type = "datetime", x_axis_label = "Time", tools=TOOLS)

    tim = [np.datetime64(i) for i in price['Date']]

    datatype = ['Close','Adj. Volume','Volume']
    for i in xrange(3):
        if datatype[i] in args.keys():
            r.line(tim, price[datatype[i]], color=colors[i], legend=company+' : '+datatype[i])

    r.title = "Stock data from Quandl WIKI set"
    r.grid.grid_line_alpha=0.3

    # Configure resources to include BokehJS inline in the document.
    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#module-bokeh.resources
    plot_resources = RESOURCES.render(
        js_raw=INLINE.js_raw,
        css_raw=INLINE.css_raw,
        js_files=INLINE.js_files,
        css_files=INLINE.css_files,
    )

    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/user_guide/embedding.html#components
    script, div = components(r, INLINE)
    html = flask.render_template(
        'result.html',
        plot_script=script, plot_div=div, plot_resources=plot_resources,
        company=company
    )
    return encode_utf8(html)


app.add_url_rule('/', 'index', lookup)
app.add_url_rule('/result', 'result', result)


def main():
    app.debug = True
    app.run()

if __name__ == "__main__":
    main()
