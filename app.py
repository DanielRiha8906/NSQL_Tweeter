from flask import Flask, render_template, request, redirect
from BackEnd.classes.user import F
from redis import Redis

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

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
    userID = redis.get("logged_in")
    if userID is None:
        return redirect('/login')
    tweets = db.myRecentTwentyTweets(int(userID))
    posts = load_20_tweets(tweets)
    return render_template('profile.html', posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = str(request.form['username'])
        passw = str(request.form['password'])
        userID = (db.loginUser(user, passw))["_id"]
        redis.hset("logged_in", str(userID))
        print(userID)
        return redirect('/profile')
    else:
        return render_template('login.html')

def load_20_tweets(tweets):
    return [
        {
            'author': tweet['userName'],
            'title': "title",
            'content': tweet['tweetContent'],
            'date_posted': tweet['dateTweeted']
        }
        for tweet in tweets
    ]


if __name__ == '__main__':
    app.run(host= "0.0.0.0", port=5000, debug=True)