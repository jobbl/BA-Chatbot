from urllib import response
from flask import Flask, render_template, request, send_file, redirect, url_for
from urllib.parse import quote
from network import synthesize, recognize, rasa_connector_rule,rasa_connector_ml, stt
import time
import os
import random
from flask_session import Session

wav_question = "question.wav"
wav_response = "response.wav"
link_ml = "https://bildungsportal.sachsen.de/umfragen/limesurvey/index.php/565864?lang=en"
link_rule = "https://bildungsportal.sachsen.de/umfragen/limesurvey/index.php/511888?lang=en"
users = {}


# initialize stt (triggers download language model for larynx/rhasspy)
while True:
    try:
        synthesize("test", wav_response)
        break
    except: continue

# create Flask instance
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/intro')
def intro():

    global users

    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr) )

    model = random.choice(['ml', 'rule'])
    users[str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))] = model

    print(model)
    if model == "ml":
        link = "https://bildungsportal.sachsen.de/umfragen/limesurvey/index.php/565864?lang=en"
    else:
        link = "https://bildungsportal.sachsen.de/umfragen/limesurvey/index.php/511888?lang=en"
    return render_template('intro.html')


# Whenever there is a request from the client to this url, run the following code
@app.route('/audio', methods=['POST', 'GET'])
def audio():

    try:
        users[str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))]
    except:
        return redirect(url_for('intro'))

    if users[str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))] == "rule":
        link = link_rule
    else:
        link = link_ml

    print("link",link)
    if request.method == "POST":
    
        response = ""
        # if client recorded audio, there will be data
        if request.data:
            with open(wav_question, mode="bw") as f:
                # write as wav, to bring in the right format for python
                f.write(request.data)

            # recognize speech with vosk
            text = stt(wav_question,"vosk-model-small-en-us-0.15")

        else:
            #  extract form data if there was any in the request
            text = str(request.form.get("question"))

        if text not in (None, '',"None"):

            if users[str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))] == "rule":
                response = rasa_connector_rule(request.environ.get('HTTP_X_REAL_IP', request.remote_addr),text)
            else:
                response = rasa_connector_ml(request.environ.get('HTTP_X_REAL_IP', request.remote_addr),text)

            if request.data:
                # encode text for synthesizing speech
                response=response.replace("#"," ")
                # synthesize speech with rhasspy, audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)
                payload = {"html": render_template(
                    'index.html', result=response, link = link)}
                return payload
            
            else:             
                return render_template('index.html', result=response, link = link)

        else:
            response = "I did not understand that. Could you please repeat?"
            if request.data:
                # encode text for synthesizing speech
                response=response.replace("#"," ")
                # synthesize speech with rhasspy,audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)
                payload = {"html": render_template(
                    'index.html', result=response, link = link)}
                return payload

    else:
        return render_template('index.html', link = link)

@app.route('/text', methods=['POST', 'GET'])
def text():

    try:
        users[str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))]
    except:
        return redirect(url_for('intro'))

    if users[str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))] == "rule":
        link = link_rule
    else:
        link = link_ml

    print("link",link)
    if request.method == "POST":
    
        response = ""
        # if client recorded audio, there will be data
        if request.data:
            with open(wav_question, mode="bw") as f:
                # write as wav, to bring in the right format for python
                f.write(request.data)

            # recognize speech with vosk
            text = stt(wav_question,"vosk-model-small-en-us-0.15")

        else:
            #  extract form data if there was any in the request
            text = str(request.form.get("question"))

        if text not in (None, '',"None"):
            if users[str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))] == "rule":
                response = rasa_connector_rule(request.environ.get('HTTP_X_REAL_IP', request.remote_addr),text)
            else:
                response = rasa_connector_ml(request.environ.get('HTTP_X_REAL_IP', request.remote_addr),text)

            if request.data:
                # encode text for synthesizing speech
                response=response.replace("#"," ")
                # synthesize speech with rhasspy, audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)
                payload = {"html": render_template(
                    'index.html', result=response, text=1, link = link)}
                return payload
            
            else:             
                return render_template('index.html', result=response, text=1, link = link)

        else:
            response = "I did not understand that. Could you please repeat?"
            if request.data:
                # encode text for synthesizing speech
                response=response.replace("#"," ")
                # synthesize speech with rhasspy,audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)
                payload = {"html": render_template(
                    'index.html', result=response, text=1, link = link)}
                return payload

    else:
        return render_template('index.html', link = link, text=1)

@app.route('/audio_response/<variable>', methods=['POST', 'GET'])
def download(variable):

    return send_file(wav_response,as_attachment=True, download_name='audio.wav')

@app.route('/', methods=['POST', 'GET'])
def redirect_to_intro():

    return redirect(url_for('intro'))

# executes when script is called -> starts the server, takes optional arguments like port number and debugging amount, see flask documentation
if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=5000,debug=True)
