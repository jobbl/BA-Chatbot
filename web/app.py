from urllib import response
from flask import Flask, render_template, request, send_file
from urllib.parse import quote
from network import synthesize, recognize, rasa_connector_rule,rasa_connector_ml, stt
import time
import os
import random

wav_question = "question.wav"
wav_response = "response.wav"
response = ""

model = ""
link = ""


# initialize stt (triggers download language model for larynx/rhasspy)
while True:
    try:
        synthesize("test", wav_response)
        break
    except: continue

# create Flask instance
app = Flask(__name__)

@app.route('/intro')
def intro():
    global model
    global link
    model = random.choice(['ml', 'rule'])
    print(model)
    if model == "ml":
        link = "ml"
    else:
        link = "rule"
    return render_template('intro.html')


# Whenever there is a request from the client to this url, run the following code
@app.route('/audio', methods=['POST', 'GET'])
def audio():

    global response

    if response == "":
        response="Start by saying \"Hello\" to me!"


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
            if model == "rule":
                response = "rule: " + rasa_connector_rule(text)
            else:
                response = "ml: " + rasa_connector_ml(text)

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
        return render_template('index.html',result=response, link = link)

@app.route('/text', methods=['POST', 'GET'])
def text():

    global response

    if response == "":
        response="Start by saying \"Hello\" to me!"

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
            if model == "rule":
                response = "rule: " + rasa_connector_rule(text)
            else:
                response = "ml: " + rasa_connector_ml(text)

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
        return render_template('index.html', result=response, link = link, text=1)

@app.route('/audio_response/<variable>', methods=['POST', 'GET'])
def download(variable):

    return send_file(wav_response,as_attachment=True, download_name='audio.wav')

# executes when script is called -> starts the server, takes optional arguments like port number and debugging amount, see flask documentation
if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=5000,debug=True)
