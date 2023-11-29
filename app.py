from flask import Flask, render_template
from BackEnd.classes.user import F

from BackEnd.classes.user import *

app = Flask(__name__)

db = F()



@app.route("/")
def home():
    tweets = db.globalRecentTwentyTweets()
    posts = [
        {
            'author': tweet['userName'],
            'title': "title",
            'content': tweet['tweetContent'],
            'date_posted': tweet['dateTweeted']
        }
        for tweet in tweets
    ]
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/profile")
def profile():
    tweets = db.myRecentTwentyTweets(userID=1)
    posts = [
        {
            'author': tweet['userName'],
            'title': "title",
            'content': tweet['tweetContent'],
            'date_posted': tweet['dateTweeted']
        }
        for tweet in tweets
    ]
    return render_template('profile.html', posts=posts)


@app.route("/login")
def register():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host= "0.0.0.0", port=5000, debug=True)