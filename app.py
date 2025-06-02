from flask import Flask, request,jsonify
from flask import render_template
import requests
from Data_Fetching.yt_comment_fetch import get_comments
from models.comment_analysis import give_analysis
from models.paragraph_analysis import give_paragraph_analysis
from transformers import pipeline
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os
app = Flask(__name__)

classifier_you_tube = pipeline('sentiment-analysis', model = 'cardiffnlp/twitter-roberta-base-sentiment')
classifier_paragraph = pipeline('text-classification',model = 'distilbert-base-uncased-finetuned-sst-2-english')
google_api_key = 'AIzaSyAUTp9GIo46szx3Az_3Nh_HOF03AH4m9qM'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/paragraph')
def paragraph():
    return render_template('paragraph.html')

@app.route('/youtube')
def youtube():
    return render_template('youtube.html')

@app.route('/fetch_comments', methods=['POST'])
def fetch_comments():
    data = request.get_json()
    video_id = data.get('youtube_id', '')
    comments = get_comments(video_id, google_api_key, requests)
    return jsonify({'comments': comments[:50]})

@app.route('/analyze_comments', methods=['POST'])
def analyze_comments():
    data = request.get_json()
    comments = data.get('comments', [])
    res = give_analysis(comments, classifier_you_tube)

    fig, ax = plt.subplots()
    ax.pie(res.values(), labels=res.keys(), autopct='%1.1f%%')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return jsonify({'graph_url': graph_url})


@app.route('/analyze_paragraph',methods = ['POST'])
def analyze_paragraph():
    paragraph = request.form['paragraph_id']
    res = give_paragraph_analysis(paragraph,classifier_paragraph)
    res = res[0]
    return render_template('paragraph_result.html',result=res)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
