a) In order to run the application, the user must have Python installed. If not, then use
this link to get started : https://docs.anaconda.com/anaconda/user-guide/getting-started/


Please install following Python packages before running the application:

1. Plotly 3.1.0 : Incase your plotly has higher version, downgrade your plotly to this version
2. ntlk: Natural language processing library for sentiment analysis
3. Dash: Latest version of dash should suffice
4. dash_boostrap_components
5. IPython Display
6. Flask
7. sqlite3
8. tweepy: this library will be used for scraping live tweets using Twitter API
9. sqlalchemy

In order to install these packages from anaconda prompt type in either of the following commands:
1. pip install <package name> 
2. pip install <package name> --user
3. conda install <package name>
4. conda install <package name> -c conda-forge

--------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------

After installing all the dependencies, we need to set up Flask apps for the four modules.
In order to do that:

1) Git clone the repository
2) Open Anaconda Prompts(4 anaconda prompts). The following process has to be applicable for 4 directories mentioned.
3) Open the respective directories of the modules(Carbon, Oil, Trader, twitter_2)
4) All of these directories should have app.py, which is our flask app(except twitter, it is names as twitter.py)
5) Windows Users, type in SET FLASK_APP=app.py, SET FLASK_ENV=development, flask run --port 900[0,3]
(change 0 for carbon, 1 for Asset, 2 for Stock and 3 for sentiments). For Mac Users, dont use SET command.
6) After your apps are initialized on the respective local hosts, go to your text editor and run iframe_apps.html.



