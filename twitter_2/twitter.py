#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import packages
import os
import datetime
import re
import nltk
import numpy as np

from collections import deque, Counter
from data_gathering.api import get_tweet_data

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State

import plotly
import plotly.graph_objs as go

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# download nltk dependencies
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')

# global refresh interval for the application, ms
GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 2000)

# initialize a sentiment analyzer
sid = SentimentIntensityAnalyzer()

keywords_to_hear = ['#climatechange',
                    '#climatestrike',
                    '#globalwarming',
                    '#parisagreement',
                    '#carbonprice',
                    '#savetheplanet'
                    ]

# stop words for the word-counts
stops = stopwords.words('english')
stops.append('https')
# for keyword in keywords_to_hear:
#     stops.append(keyword)

# initialize the app and server
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server

# global color setting
app_color = {
    "graph_bg": "rgb(40, 40, 40)",
    "graph_line": "rgb(244, 244, 244)",
    "graph_font":"rgb(255, 255, 255)"
}

# colors for plots
chart_colors = [
    '#664DFF',
    '#893BFF',
    '#3CC5E8',
    '#2C93E8',
    '#0BEBDD',
    '#0073FF',
    '#00BDFF',
    '#A5E82C',
    '#FFBD42',
    '#FFCA30'
]

# the number of most frequently mentioned tags
num_tags_scatter = 5

# initalize a dictionary to store the number of tweets for each game
scatter_dict = {}

sentiment_dict = {}

# initialize x and y coordinates for scatter plot
# use duque here to store the changing trend of number of tweets
# X is the x-axis with time stamps
X_universal = deque(maxlen=30)

# add layout to the app
app.layout = html.Div(
    [
        # header
        html.Div(
            [   
                html.Div([
                    html.H1(id='header', children='SENTIMENT ANALYSIS'),
                    html.Div(id='sub-header'),
                    html.Br(),
                    html.Div([
                        html.Span(children='''Sentiments will allow users to identify the social impacts of conversations on social media. 
                        The platform measures engagements, mentions, and word counts to a sentiment score that compares different trending 
                        hashtags. Users may use the information to make stock predictions or in development of financial instruments that takes 
                        into consideration climate related issues.''')
                    
                    ], id="intro"),
                ], id='intro-section'),
            ],
            className="app__header",
        ),
        html.Div(
            [
                # left hand side, tweets count scatter plot
                html.Div(
                    [   
                        dcc.Interval(
                            id="query_update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                        html.Div(
                            [html.H6("WORD-COUNT TREND", className="graph__title")]
                        ),
                        html.Div(
                                    [
                                        html.P(
                                            "Total number of tweets streamed during last 60 seconds: 0",
                                            id="bin-size",
                                            className="auto__p",
                                        ),
                                    ],
                                    className="auto__container",
                                ),
                        dcc.Graph(
                            id="number_of_tweets",
                            animate=False,
                            figure=go.Figure(
                                layout=go.Layout(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                    ],
                    className="two-thirds column number_of_tweets",
                ),
                # right hand side, bar plot and pie chart
                html.Div(
                    [
                        # bar chart
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "WORD COUNT",
                                            className="graph__title",
                                        )
                                    ]
                                ),
                                dcc.Graph(
                                    id="word_counts",
                                    animate=False,
                                    figure=go.Figure(
                                        layout=go.Layout(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            className="graph__container first",
                        ),
                        # sentiment plot
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "SENTIMENT SCORE", className="graph__title"
                                        )
                                    ]
                                ),
                                dcc.Graph(
                                    id="sentiment_scores",
                                    figure=go.Figure(
                                        layout=go.Layout(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            className="graph__container second",
                        ),
                    ],
                    className="one-third column bar_pie",
                ),
            ],
            className="app__content",
        ),
        # footer
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            '''Climate community*: the keywords tracked by the streaming server includes: #climatechange,#climatestrike, 
                            #globalwarming, #parisagreement,#carbonprice, #savetheplanet''',
                            className="app__comment",
                        ),
                    ]
                    
                )
            ]
        )
    ],
    className="app__container",
)

def hashtag_counter(series):
    """
    count the number of tweets for all the keywords

    Parameters
    ----------
        seriers: pandas Series
            the text column that contains the text of the tweets
    
    Returns
    -------
        cnt: dictionary
            a dictionary with keyword: number of tweets
    """

    cnt = {keyword: 0 for keyword in keywords_to_hear}
    for row in series:
        for keyword in keywords_to_hear:    
            if keyword.lower() in row.lower():
                cnt[keyword] += 1
    return cnt


def bag_of_words(series):
    """
    count the words in all the tweets

    Parameters
    ----------
        seriers: pandas Series
            the text column that contains the text of the tweets

    Returns
    -------
        collections.Counter object
            a dictionary with all the tokens and their number of apperances
    """
    
    # merge the text from all the tweets into one document
    document = ' '.join([row for row in series])

    # lowercasing, tokenization, and keep only alphabetical tokens
    tokens = [word for word in word_tokenize(document.lower()) if word.isalpha()]

    # filtering out tokens that are not all alphabetical
    tokens = [word for word in re.findall(r'[A-Za-z]+', ' '.join(tokens))]

    # remove all stopwords
    no_stop = [word for word in tokens if word not in stops]

    return Counter(no_stop)

def preprocess_nltk(row):
    """
    preprocessing the user description for user tagging

    Parameters
    ----------
        row: string
            a single record of a user's profile description
    
    Returns
    -------
        string
            a clean string
    """

    # lowercasing, tokenization, and keep only alphabetical tokens
    tokens = [word for word in word_tokenize(row.lower()) if word.isalpha()]

    # filtering out tokens that are not all alphabetical
    tokens = [word for word in re.findall(r'[A-Za-z]+', ' '.join(tokens))]

    # remove all stopwords
    no_stop = [word for word in tokens if word not in stops]

    return ' '.join(no_stop)


# define callback function for number_of_tweets scatter plot
@app.callback(
    Output('number_of_tweets', 'figure'),
    [Input('query_update', 'n_intervals')])
def update_graph_scatter(n):

    # query tweets from the database
    DB_FILE = 'tweets.db'
    df = get_tweet_data(DB_FILE)

    # get the number of tweets for each keyword
    cnt = bag_of_words(df['text'])

    # get the current time for x-axis
    time = datetime.datetime.now().strftime('%D, %H:%M:%S')
    X_universal.append(time)

    to_pop = []
    for keyword, cnt_queue in scatter_dict.items():
        if cnt_queue:
            while cnt_queue and (cnt_queue[0][1] < X_universal[0]):
                cnt_queue.popleft()
        else:
            to_pop.append(keyword)
        

    for keyword in to_pop:
        scatter_dict.pop(keyword)

    top_N = cnt.most_common(num_tags_scatter)

    for keyword, cnt in top_N:
        if keyword not in scatter_dict:
            scatter_dict[keyword] = deque(maxlen=30)
            scatter_dict[keyword].append([cnt, time])
        else:
            scatter_dict[keyword].append([cnt, time])

    new_colors = chart_colors[:len(scatter_dict)]

    # plot the scatter plot
    data=[go.Scatter(
        x=[time for cnt, time in cnt_queue],
        y=[cnt for cnt, time in cnt_queue],
        name=keyword,
        mode='lines+markers',
        opacity=0.5,
        marker=dict(
            size=10,
            color=color,
        ),
        line=dict(
            width=6,
            # dash='dash',
            color=color,
        )
    ) for color, (keyword, cnt_queue) in list(zip(new_colors, scatter_dict.items()))]

    # specify the layout
    layout = go.Layout(
            xaxis={
                'automargin': False,
                'range': [min(X_universal), max(X_universal)],
                'title': 'Current Time (GMT)',
                'nticks': 6
            },
            yaxis={
                'type': 'log',
                'autorange': True,
                'title': 'Number of Tweets'
            },
            height=700,
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": app_color["graph_font"]},
            autosize=False,
            legend={
                'orientation': 'h',
                'xanchor': 'center',
                'yanchor': 'top',
                'x': 0.5,
                'y': 1.025
            },
            margin=go.layout.Margin(
                l=75,
                r=25,
                b=45,
                t=25,
                pad=4
            ),
        )

    return go.Figure(
        data=data,
        layout=layout,
    )

# define callback function for word-counts
@app.callback(
    Output('word_counts', 'figure'),
    [Input('query_update', 'n_intervals')])
def update_graph_bar(interval):

    # query tweets from the database
    DB_FILE = 'tweets.db'
    df = get_tweet_data(DB_FILE)

    # get the counter for all the tokens
    word_counter = bag_of_words(df.text)

    # get the most common n tokens
    # n is specified by the slider
    top_n = word_counter.most_common(10)[::-1]

    # get the x and y values
    X = [cnt for word, cnt in top_n]
    Y = [word for word, cnt in top_n]

    # plot the bar chart
    bar_chart = go.Bar(
        x=X, y=Y,
        name='Word Counts',
        orientation='h',
        marker=dict(color=chart_colors[::-1])
    )

    # specify the layout
    layout = go.Layout(
            xaxis={
                'type': 'log',
                'autorange': True,
                'title': 'Number of Words'
            },
            height=300,
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": app_color["graph_font"]},
            autosize=True,
            margin=go.layout.Margin(
                l=100,
                r=25,
                b=75,
                t=25,
                pad=4
            ),
        )

    return go.Figure(
        data=[bar_chart], layout=layout
    )

# define callback function for user_group
@app.callback(
    Output('sentiment_scores', 'figure'),
    [Input('query_update', 'n_intervals')])
def update_graph_sentiment(interval):

    # query tweets from the database
    DB_FILE = 'tweets.db'
    df = get_tweet_data(DB_FILE)
    # get the number of tweets for each keyword
    cnt = bag_of_words(df['text'])

    # get top-N words
    top_N = cnt.most_common(num_tags_scatter)
    top_N_words = [keyword for keyword, cnt in top_N]


    # preprocess the text column
    df['text'] = df.text.apply(preprocess_nltk)

    sentiments = {keyword:[] for keyword in top_N_words}
    for row in df['text']:
        # print(row)
        for keyword in top_N_words:
            # print(keyword)
            if keyword.lower() in row.lower():
                # print(sid.polarity_scores(row)['compound'])
                sentiments[keyword].append(sid.polarity_scores(row)['compound'])
    
    # print(sentiments)
    
    avg_sentiments = {}
    for keyword, score_list in sentiments.items():
        avg_sentiments[keyword] = [np.mean(score_list), np.std(score_list)]
    
    # get the current time for x-axis
    time = datetime.datetime.now().strftime('%D, %H:%M:%S')
    X_universal.append(time)

    to_pop = []
    for keyword, score_queue in sentiment_dict.items():
        if score_queue:
            while score_queue and (score_queue[0][1] <= X_universal[0]):
                score_queue.popleft()
        else:
            to_pop.append(keyword)
        

    for keyword in to_pop:
        sentiment_dict.pop(keyword)

    for keyword, score in avg_sentiments.items():
        if keyword not in sentiment_dict:
            sentiment_dict[keyword] = deque(maxlen=30)
            sentiment_dict[keyword].append([score, time])
        else:
            sentiment_dict[keyword].append([score, time])

    new_colors = chart_colors[:len(sentiment_dict)]

    # plot the scatter plot
    data=[go.Scatter(
        x=[time for score, time in score_queue],
        y=[score[0] for score, time in score_queue],
        error_y={
            "type": "data",
            "array": [score[1]/30 for score, time in score_queue],
            "thickness": 1.5,
            "width": 1,
            "color": "#000",
        },
        name=keyword,
        mode='markers',
        opacity=0.7,
        marker=dict(color=color)
    ) for color, (keyword, score_queue) in list(zip(new_colors, sentiment_dict.items()))]

    # specify the layout
    layout = go.Layout(
            xaxis={
                'automargin': False,
                'range': [min(X_universal), max(X_universal)],
                'title': 'Current Time (GMT)',
                'nticks': 2,
            },
            yaxis={
                'autorange': True,
                'title': 'Sentiment Score'
            },
            height=400,
            plot_bgcolor=app_color["graph_bg"],
            paper_bgcolor=app_color["graph_bg"],
            font={"color": app_color["graph_font"]},
            autosize=False,
            legend={
                'orientation': 'v',
                # 'xanchor': 'right',
                # 'yanchor': 'middle',
                # 'x': 0.5,
                # 'y': 1.025
            },
            margin=go.layout.Margin(
                l=75,
                r=25,
                b=70,
                t=25,
                pad=4
            ),
        )

    return go.Figure(
        data=data,
        layout=layout,
    )


# define callback functions for the indicator of the slider
@app.callback(
    Output("bin-size", "children"),
    [Input("query_update", "n_intervals")],
)
def show_num_bins(slider_value):
    """ Display the number of bins. """

    DB_FILE = 'tweets.db'
    df = get_tweet_data(DB_FILE)
    total_tweets = len(df)

    return "Total number of tweets streamed during last 60 seconds: " + str(int(total_tweets))

# run the app
if __name__ == '__main__':
    app.run_server(port=8001,debug=True)