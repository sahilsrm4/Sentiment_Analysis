from flask import Flask, request,jsonify
from flask import render_template
import requests
from Data_Fetching.yt_comment_fetch import get_comments
from models.comment_analysis import give_analysis
from models.paragraph_analysis import give_paragraph_analysis
from transformers import pipeline
import matplotlib.pyplot as plt
import io
import base64
app = Flask(__name__)

google_api_key = 'AIzaSyAUTp9GIo46szx3Az_3Nh_HOF03AH4m9qM'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze_youtube', methods = ['POST'])
def analyze_youtube():
    video_id = request.form['youtube_id']

    comments = get_comments(video_id,google_api_key,requests)
    res = give_analysis(comments[:100],pipeline)
    # plot pie chart
    fig , ax = plt.subplots()
    ax.pie(res.values(), labels = res.keys(),autopct='%1.1f%%',colors=['green','blue','red'])
    ax.set_title("Analysis Summary")

    # Save to Buffer
    buf = io.BytesIO()
    plt.savefig(buf, format ='png')
    buf.seek(0)
    graph_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return render_template('youtube_result.html',graph_url=graph_url)

@app.route('/analyze_paragraph',methods = ['POST'])
def analyze_paragraph():
    paragraph = request.form['paragraph_id']
    res = give_paragraph_analysis(pipeline,paragraph)
    res = res[0]
    return render_template('paragraph_result.html',result=res)

if __name__ == '__main__':
    app.run()