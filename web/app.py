from urllib import response
from flask import Flask, render_template, request, send_file, redirect, url_for, make_response
from urllib.parse import quote
from network import synthesize, recognize, rasa_connector_rule,rasa_connector_ml, stt
import time
import os
import random
from flask_session import Session
from flask_talisman import Talisman

wav_question = "question.wav"
wav_response = "response.wav"
link_ml = "https://bildungsportal.sachsen.de/umfragen/limesurvey/index.php/331853?lang=en"
link_rule = "https://bildungsportal.sachsen.de/umfragen/limesurvey/index.php/752773?lang=en"
users = []


# initialize stt (triggers download language model for larynx/rhasspy)
while True:
    try:
        synthesize("test", wav_response)
        break
    except: continue

# create Flask instance
app = Flask(__name__)
Talisman(app, content_security_policy=None)
Session(app)

@app.route('/intro')
def intro():

    global users

    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr) )

    model = random.choice(['ml', 'rule'])
    # users[str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))] = model

    resp = make_response(render_template('intro.html'))
    resp.set_cookie('model', model)
    resp.set_cookie('mode', "audio")
    # delete last_response
    resp.set_cookie('last_response', '', expires=0)


    id = random.randint(0,10000000)
    while id in users:
        id = random.randint(0,10000000)
    users.append(str(id))
    resp.set_cookie('id', str(id))

    return resp 
    # return render_template('intro.html')


# Whenever there is a request from the client to this url, run the following code
@app.route('/', methods=['POST', 'GET'])
def index():

    print(request.cookies.get('model'),request.cookies.get('mode'),request.cookies.get('id'),request.cookies.get('last_response'))
    if request.cookies.get('last_response'):
        last_response = request.cookies.get('last_response')
    else:
        last_response = "Start by saying 'Hello' to me!"

    if request.cookies.get('id') not in users:
        return redirect(url_for('intro'))

    if request.cookies.get('model') == "rule":
        link = link_rule
    else:
        link = link_ml

    if request.cookies.get('mode') == "text":
        text_input = 1
    else:
        text_input = None

    if request.method == "POST":
    
        response = ""
        # if client recorded audio, there will be data
        if request.data:
            with open(wav_question, mode="bw") as f:
                # write as wav, to bring in the right format for python
                f.write(request.data)

            # recognize speech with vosk - small model
            text = stt(wav_question,"vosk-model-small-en-us-0.15")

        else:
            #  extract form data if there was any in the request
            text = str(request.form.get("question"))

        if text not in (None, '',"None"):

            if request.cookies.get('model') == "rule":
                response = rasa_connector_rule(request.cookies.get('id'),text)
            else:
                response = rasa_connector_ml(request.cookies.get('id'),text)

            last_response = response
            
            print("The user said:",text)
            print("RASA answered:",response)


            # response = rasa_connector_rule(request.cookies.get('id'),text)
            # if response[1] not in (None, '',"None"):
            #     print("here")
            #     response = response[1]
            # else:
            #     print("there")
            #     response = response[0]
            # print(response)

            if request.data:
                # encode text for synthesizing speech
                response=response.replace("#"," ")
                # synthesize speech with rhasspy, audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)
                payload = {"html": render_template(
                    'index.html', result=response, link = link,text = text_input, last_response=last_response)}

                resp = make_response(payload)
                resp.set_cookie('last_response', last_response)
                return resp
            
            else:             
                
                resp = make_response(render_template('index.html', result=response, link = link, text = text_input, last_response=last_response))
                resp.set_cookie('last_response', last_response)
                return resp

        else:
            response = "I did not understand that. Could you please repeat?"
            if request.data:
                # encode text for synthesizing speech
                response=response.replace("#"," ")
                # synthesize speech with rhasspy,audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)
                payload = {"html": render_template(
                    'index.html', result=response, link = link,text = text_input, last_response=last_response)}
                resp = make_response(payload)
                resp.set_cookie('last_response', last_response)
                return resp

    else:
        resp = make_response(render_template('index.html', link = link,text = text_input, last_response=last_response))
        resp.set_cookie('last_response', last_response)
        return resp


@app.route('/text', methods=['POST', 'GET'])
def text():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('mode', "text")
    return resp

@app.route('/audio', methods=['POST', 'GET'])
def audio():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('mode', "audio")
    return resp

@app.route('/audio_response/<variable>', methods=['POST', 'GET'])
def download(variable):

    return send_file(wav_response,as_attachment=True, download_name='audio.wav')

@app.route('/help', methods=['POST', 'GET'])
def help():

    return render_template('help.html')

@app.route('/restart', methods=['POST', 'GET'])
def restart():

    resp = make_response(redirect(url_for('intro')))
    return resp

# executes when script is called -> starts the server, takes optional arguments like port number and debugging amount, see flask documentation
if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=5000,debug=True)
