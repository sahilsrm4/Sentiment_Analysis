from flask import Flask, request,jsonify
from flask import render_template
from flask import session
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
import mysql.connector
import datetime
import re
app = Flask(__name__)

classifier_you_tube = pipeline('sentiment-analysis', model = 'cardiffnlp/twitter-roberta-base-sentiment')
classifier_paragraph = pipeline('text-classification',model = 'distilbert-base-uncased-finetuned-sst-2-english')
google_api_key = 'AIzaSyAUTp9GIo46szx3Az_3Nh_HOF03AH4m9qM'

app.secret_key = '9068'


def connect_db():
        conn = mysql.connector.connect(
            host = "localhost",
            user = 'root',
            password = '9068$$$$pppP',
            database = "feel_fetch"
        )
        return conn

@app.route('/')
def index():
    user_id = session.get('user_id')
    return render_template('index.html',user_id = user_id)

@app.route('/paragraph')
def paragraph():
    return render_template('paragraph.html')

@app.route('/youtube')
def youtube():
    return render_template('youtube.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'] )
def login():
    name = request.form.get('username')
    password = request.form.get('password')

    conn = connect_db()
    cursor = conn.cursor()
    query = 'select * from users where name = %s'
    cursor.execute(query,(name,))
    print('Name is:', name)
    print('Password is:', password)
    res = cursor.fetchall()
    print('Fetched Data ',res)
    if res:
        if password == res[0][2]:
            session['user_id'] = res[0][0]
            user_id = session.get('user_id')
            print('Login Succesfull')
            return render_template('index.html',user_id=user_id)
        else:
            print("Wrong password")
            return render_template('login.html', error="Wrong password")
    else:
        print("No user exist with this name")
        return render_template('login.html', error="No user exists with this name")
    
@app.route('/signup', methods = ['POST'])
def signup():
    name = request.form.get('username')
    password = request.form.get('password')
    conn = connect_db()
    query = 'select * from users where name = %s'
    cursor = conn.cursor()
    cursor.execute(query,(name,))
    res = cursor.fetchall()
    if res:
        return render_template('login.html', error="User Name Already Exist")
    query = 'insert into users(name, password) values(%s , %s)'
    cursor.execute(query,(name,password))
    conn.commit()
    return render_template('login.html')

@app.route('/fetch_comments', methods=['POST'])
def fetch_comments():
    import re

    def extract_youtube_id(url):
           pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|v/)|youtu\.be/)([a-zA-Z0-9_-]{11})'
           match = re.search(pattern, url)
           return match.group(1) if match else None

 
    data = request.get_json()
    url = data.get('youtube_id', '')
    session['video_id'] = extract_youtube_id(url)
    video_id = session.get('video_id')
    comments = get_comments(video_id, google_api_key, requests)
    return jsonify({'comments': comments[:50]})

@app.route('/analyze_comments', methods=['POST'])
def analyze_comments():
    video_id = session.get('video_id')
    user_id = session.get('user_id')
    data = request.get_json()
    comments = data.get('comments', [])
    res = give_analysis(comments, classifier_you_tube)
    score = res['Positive']+res['Neutral']-res['Negative']
    if user_id:
        conn = connect_db()
        cursor = conn.cursor()
        query = 'insert into video_analysis(user_id,video_id,score) values(%s,%s,%s)'
        cursor.execute(query,(user_id,video_id,score))
        conn.commit()
        cursor.close()

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

@app.route('/progress')
def graph():
     user_id = session.get('user_id')
     if user_id != None:
        conn = connect_db()

        cursor = conn.cursor()

        query = "select * from video_analysis where user_id = %s"
        cursor.execute(query,(user_id,))
        result = cursor.fetchall()

        score = []
        time = []
        for row in result:
           score.append(row[3])
           time.append(row[4])
    

        fig, ax = plt.subplots(figsize = (12,6))
        ax.plot(time, score, marker='o', linestyle='-', color='b')
        ax.set_title('Progress Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Score')

        # Save the plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Encode to base64 string for embedding
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return render_template('progress.html', graph_image=encoded)
     else:
         return render_template('login_first.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port,debug=True)
