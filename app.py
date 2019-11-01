from flask import Flask, render_template, request

from wtforms import Form, TextAreaField, validators

import requests
import numpy as np 
import re
import os
import json
import plotly


import plotly.graph_objs as go
import pandas as pd


class Graph():

    def create_plot_bar(self, list_=[1, 1]):

        data = [
            go.Bar(
                y=list_,
            )
        ]
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON

    def create_plot(self, feature='Bar'):
        if feature == 'Bar':
            N = 40
            x = np.linspace(0, 1, N)
            y = np.random.randn(N)
            df = pd.DataFrame({'x': x, 'y': y})  # creating a sample dataframe
            data = [
                go.Bar(
                    x=df['x'],  # assign x as the dataframe column 'x'
                    y=df['y']
                )
            ]
        else:
            N = 1000
            random_x = np.random.randn(N)
            random_y = np.random.randn(N)

            # Create a trace
            data = [go.Scatter(
                x=random_x,
                y=random_y,
                mode='markers'
            )]

        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON



class HelloForm(Form):
    sayhello = TextAreaField('', [validators.DataRequired()], render_kw={'rows': 1, 'cols': 60})

app = Flask(__name__)

dirname = os.path.dirname(__file__)

class Helper():
    def __init__(self):
        self.video_id = ''
        self.r = {}


    def get_video_id(self, url):
        self.video_id = url.split('=')[1]
    
    def get_respons_jsone(self):

        url = 'https://www.googleapis.com/youtube/v3/commentThreads'

        key_api = 'AIzaSyC6mUfTewPh2ZPZHUFWbYu45J7dSI4PKOk'
        some_part = 'snippet'
        self.r = requests.get(url=url, params={'videoId': self.video_id,
                                                'key':key_api, 
                                                'part':some_part,
                                                'maxResults':100, 
                                                })
        self.save_to_json_file()

    def save_to_json_file(self):
        with open(os.path.join(dirname, 'respons.json'), 'w') as f:
            json.dump(self.r.json(), f, indent=2, ensure_ascii=False)

    def get_comments(self):
        json_file_ = os.path.join(dirname, 'respons.json')
        data = json.load(open(json_file_))
        dict_comments = [i['snippet']['topLevelComment']['snippet']['textDisplay'] for i in data['items']]

        return dict_comments[self.index]

    def get_all_comments(self):
        json_file_ = os.path.join(dirname, 'respons.json')
        data = json.load(open(json_file_))
        list_comments = [i['snippet']['topLevelComment']['snippet']['textDisplay'] for i in data['items']]
        return list_comments

    def write_int_next(self):
        with open(os.path.join(dirname, 'int.txt'), 'w') as f:
            f.write(str(self.index+1))

    def write_int_before(self):
        with open(os.path.join(dirname, 'int.txt'), 'w') as f:
            f.write(str(self.index-1))
    
    def read_int(self):
        with open(os.path.join(dirname, 'int.txt'), 'r') as f:
            self.index = int(f.read())
            if self.index < 0:
                self.index = 0
        return self.index

    def init_int(self):
        self.index = 0
        self.write_int_next()

    def get_respons_url_from_djrest(self):
        url = 'http://adilhan.pythonanywhere.com/api/v1/app/urls_video_youtube/'
        r_djrest = requests.get(url=url)
        data_list = [[i['video_id'], i['name_video'], i['id']] for i in r_djrest.json()['data']]

        return data_list

    def post_respons_url_from_djrest(self, video_id):
        url = 'http://adilhan.pythonanywhere.com/api/v1/app/urls_video_youtube/'
        respons = requests.post(url=url, data={'video_id': video_id})
        return respons.json()

    def post_comment_for_djrest(self, video='1', comment='text', assessnment='0'):
        url = 'http://adilhan.pythonanywhere.com/api/v1/app/comments/'
        requests.post(url, data={'video':video, 'comment':comment, 'assessment': assessnment})

    def write_id(self, id_):
        with open(os.path.join(dirname, 'id.txt'), 'w') as f:
            f.write(str(id_))
        pass

    def read_id(self):
        with open(os.path.join(dirname, 'id.txt'), 'r') as f:
            id_ = int(f.read())
        return id_
    

# @app.route('/')
# def init():
#     return render_template('first_app.html')

@app.route('/bar', methods=['GET', 'POST'])
def change_features():
    graph = Graph()

    feature = request.args['selected']
    graphJSON= graph.create_plot(feature)
    return graphJSON

@app.route('/', methods=['GET','POST'])
def hello_ml():
    form = HelloForm(request.form)

    helper = Helper()

    graph = Graph()
#
    try:
#
        if request.method == 'POST' and form.validate():
            name = request.form['sayhello']

            respons = helper.post_respons_url_from_djrest(video_id=name)
            positive = []
            negative = []
            name_ = [[respons[i]['comment'], respons[i]['essessment']]for i in respons]
            for i in respons:
                num = respons[i]['essessment']
                if num == 0:
                    negative.append(num)
                else:
                    positive.append(num)

            bar = graph.create_plot_bar(list_=[len(negative), len(positive)])
            form = HelloForm()

            return render_template('hello_ml.html',
                                   name=[len(negative), len(positive)],
                                   plot=bar,
                                   form=form)
    #
        else:
            bar = graph.create_plot_bar()
            form = HelloForm()
            return render_template('hello_ml.html',
                                   name=[1,1],
                                   plot=bar,
                                   form=form)

    except:
        bar = graph.create_plot_bar()
        form = HelloForm()
        return render_template('hello_ml.html',
                               name='Количество отрицательных(0) и положительных(1) отзывов',
                               plot=bar,
                               form=form)


@app.route('/post_ml')
def post_ml():
    return render_template('get_url_from_djangorest.html')

@app.route('/hello_url', methods=['POST'])
def hello_url():

    helper = Helper()

    if request.method == 'POST':
        feedback = request.form['feedback']
        if feedback == 'Get urls from django rest_framework':
            data_list = helper.get_respons_url_from_djrest()

            return render_template('hello_url.html', urls=data_list)
        else:
            return render_template('get_url_from_djangorest.html')

    return render_template('get_url_from_djangorest.html')

@app.route('/hello', methods=['POST'])
def hello():
    helper = Helper()
    feedback_url = request.form['feedback_buttom']
    # try:
    if request.method == 'POST' and 'youtube' in feedback_url:
        name = request.form['feedback_buttom']
        id_ = request.form['id_']

        helper.get_video_id(name)
        helper.write_id(id_)

        helper.get_respons_jsone()
        helper.init_int()
        comment = helper.get_comments()

        return render_template('hello.html', name=comment)

    elif request.method == 'POST':
        feedback = request.form['feedback_buttom']
        if feedback == 'Next':
            helper.read_int()
            comment = helper.get_comments()
            helper.write_int_next()
            return render_template('hello.html', name=comment)
        elif feedback == 'Before':
            helper.read_int()
            comment = helper.get_comments()
            helper.write_int_before()
            return render_template('hello.html', name=comment)
        elif feedback == 'Positive':
            comment = request.form['comment']
            assessment = '1'
            id_ = helper.read_id()

            helper.post_comment_for_djrest(video=id_, comment=comment, assessnment=assessment)

            helper.read_int()
            comment = helper.get_comments()
            helper.write_int_next()
            return render_template('hello.html', name=comment)
        elif feedback == 'Negative':
            comment = request.form['comment']
            assessment = '0'
            id_ = helper.read_id()

            helper.post_comment_for_djrest(video=id_, comment=comment, assessnment=assessment)

            helper.read_int()
            comment = helper.get_comments()
            helper.write_int_next()
            return render_template('hello.html', name=comment)

        return render_template('get_url_from_djangorest.html')


    return render_template('get_url_from_djangorest.html')

    # except:
    #     return render_template('get_url_from_djangorest.html')

if __name__ == '__main__':
    app.run(debug=True)