from flask import Flask, render_template
from flask import render_template, request, redirect, url_for
from datetime import datetime
import requests
import praw
import json
import chartjs
import os

app = Flask(__name__)

# HOME VIEW
@app.route("/", methods=["POST","GET"])
def home():
    if request.method == "POST":
        return redirect(url_for("predict"))
    else:
        return render_template("home-form.html")


# VIEW TO FETCH DATA FROM REDDIT AND POST TO SAGEMAKER ENDPOINT
@app.route("/predict", methods=["POST","GET"])
def predict():

    # PULL SUBMISSIONS FROM REDDIT API
    RED_CLIENT_ID = os.environ.get('RED_CLIENT_ID', 'not_set')
    RED_CLIENT_SECRET = os.environ.get('RED_CLIENT_SECRET', 'not_set')
    RED_USER_AGENT = os.environ.get('RED_USER_AGENT', 'not_set')

    # praw object with credentials that returns reddit data
    reddit = praw.Reddit(
    client_id=RED_CLIENT_ID,
    client_secret=RED_CLIENT_SECRET,
    redirect_uri="http://localhost:8000",
    user_agent=RED_USER_AGENT)

    # fetch the 20 hottest submissions across all subreddits
    titles = set()
    for sub in reddit.subreddit("politics").hot(limit=20):
        titles.add(sub.title)

    # cast titles as list
    titles = list(titles)

    # payload of Reddit submissions to use for inference from sagemaker enpoint via API Gateway
    payload = {"text": titles}

    # make post request to AWS Sagemaker Endpoint
    headers = {'Content-Type': 'application/json'}
    response = requests.post("https://9le09xvq8l.execute-api.us-east-1.amazonaws.com/first-stage/sentiment", json=payload, headers=headers)

    # cast json response from AWS Lambda to dictionary
    sentiments = json.loads(response.json())
    
    # encode 0, 1 integer response to negative and postive strings, respectively
    parsed_sentiment = ["positive" if lbl == 1 else "negative" for lbl in sentiments['sentiment']]

    # pair submissions and predicted sentiments in an iterable of tuples
    result_tuple = zip(titles, parsed_sentiment)

    #prelim_result = zip(arr_text, sentiment)
    pos_ls_tp = []
    neg_ls_tp = []
    
    for tuple in result_tuple:
        if tuple[1] == "positive":
            pos_ls_tp.append(tuple)
        else:
            neg_ls_tp.append(tuple)
    
    date_time = datetime.now()
        
    # simulate draw a barchart of sentiments
    labels = ['Positive','Negative']
    data = [len(pos_ls_tp), len(neg_ls_tp)]

    return render_template("predict.html", pos_content=pos_ls_tp, neg_content=neg_ls_tp, date=date_time, labels=labels, data=data)

 
if __name__ == "__main__": 
    app.run(debug=False, port=8000)
