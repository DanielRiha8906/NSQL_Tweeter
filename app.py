from flask import Flask, render_template

app = Flask(__name__)

posts = [
    {
        'author': 'Alexander',
        'title': 'Pp poo poo',
        'content': 'It realy do be',
        'date_posted': '25. November 2023'
    },
    {
        'author': 'Daniel',
        'title': 'yes',
        'content': 'Thoughout the history there has been some bullshit, that I am just writing to get a sense of how does it work rn regarding the structure of the text.com',
        'date_posted': '26. November 2023'
    },
    {
        'author': 'Adam',
        'title': 'nope',
        'content': 'coke',
        'date_posted': '27. November 2023'
    }
]

@app.route("/")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/register")
def register():
    return render_template('register.html')



if __name__ == '__main__':
    app.run(host= "0.0.0.0", port=5000, debug=True)