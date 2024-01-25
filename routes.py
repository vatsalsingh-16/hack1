# app/routes.py

from flask import render_template, request, jsonify
from model.sentiment_model import predict_sentiment
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    tweet = request.form['tweet']
    result = predict_sentiment(tweet)
    return render_template('index.html', tweet=tweet, result=result)