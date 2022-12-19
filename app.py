import os
import uuid
import flask
import urllib

from flask import Flask , render_template  , request , send_file

import pandas as pd

import clarinService as c

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def home():
        return render_template("index.html")

@app.route('/errorPage')
def error():
        return render_template("errorPage.html")

@app.route('/success' , methods = ['GET' , 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd() , 'static/images')
    if request.method == 'POST':
        if(request.form):
            try :
                text = request.form.get('text')
                servie = c.ClarinService(text)
                response_frame = servie.run()
                if len(response_frame) == 0 or 'Polarity' not in response_frame.columns.to_list():
                    return render_template('errorPage.html')
                polarity = response_frame[response_frame['Polarity'] != 'None']['Polarity']
                polarity = polarity.apply(lambda row: pd.to_numeric(row, errors='coerce'))
                pd.Series.dropna(polarity, inplace =True)
                result = polarity.sum()
                if result < 0:
                    ans = 'Negative'
                elif result == 0:
                    ans = 'Neutral'
                else:
                    ans = 'Positve'
                return  render_template('success.html' , result = result, ans = ans)
            except Exception as e : 
                print(str(e))
               

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug = True)


