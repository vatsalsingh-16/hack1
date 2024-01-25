from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from model.sentiment_model import predict_sentiment

app = Flask(__name__, template_folder='app/templates')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'risk_control'

mysql = MySQL(app)

# List to store entered tweets
all_tweets = []

def count_sentiments():
    total_positive = sum(1 for tweet_entry in all_tweets if tweet_entry['result'] == 1)
    total_negative = sum(1 for tweet_entry in all_tweets if tweet_entry['result'] == 0)
    return total_positive, total_negative

@app.route('/')
def index():
    total_positive, total_negative = count_sentiments()

    # Retrieve all tweets from the tweets table
    cur = mysql.connection.cursor()
    cur.execute("SELECT tweet, sentiment FROM tweets")
    user_tweets = cur.fetchall()
    cur.close()

    return render_template('index.html', all_tweets=all_tweets, total_positive=total_positive,
                           total_negative=total_negative, user_tweets=user_tweets)

@app.route('/predict', methods=['POST'])
def predict():
    tweet = request.form['tweet']
    username = request.form['username']

    # Your sentiment prediction logic goes here
    sentiment = predict_sentiment(tweet)  # Implement your sentiment prediction function

    # Get user_id from the users table based on the username
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    user_id = cur.fetchone()
    cur.close()

    if user_id:
        # Store the tweet with the corresponding user_id, username, and sentiment in the tweets table
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tweets (user_id, username, tweet, sentiment) VALUES (%s, %s, %s, %s)",
                    (user_id[0], username, tweet, sentiment))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))
    else:
        return "User not found."

@app.route('/user_tweets', methods=['GET', 'POST'])
def user_tweets():
    if request.method == 'POST':
        username = request.form['username']

        # Fetch tweets and sentiments for the given username
        cur = mysql.connection.cursor()
        cur.execute("SELECT tweet, sentiment FROM tweets WHERE username = %s", (username,))
        user_tweets = cur.fetchall()
        cur.close()

        return render_template('user_tweets.html', username=username, user_tweets=user_tweets)

    return render_template('user_tweets_input.html')

if __name__ == '__main__':
    app.run(debug=True)
