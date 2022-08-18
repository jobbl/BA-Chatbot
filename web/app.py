from urllib import response
from flask import Flask, render_template, request, send_file
from urllib.parse import quote
from network import synthesize, recognize, rasa_connector_rule,rasa_connector_ml, stt
import time
import os
import random

wav_question = "question.wav"
wav_response = "response.wav"

model = ""
link = ""

intro = "Welcome! You have found your way to an experiment about an emotion understanding therapy bot. At least thats the aim ^^. \n First, The bot will guide you through a little conversation of about 5 minutes. At the end it will ask you to follow a link to a short survey, which also takes about 5 minutes. Everything is totally anonymous. The things you say during the session are not saved, and the survey is anonymous. \n When you are ready, make sure you are not muted and then press on the \"Record\" Button. The browser will ask you for microphone permissions, if have not given them already. When you are done speaking, the bot will take a while to process and then answer you. Have fun!   "

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
@app.route('/', methods=['POST', 'GET'])
def extract():
    
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
                    'index.html', result=response, text=text, link = link)}
                return payload
            
            else:             
                return render_template('index.html', result=response, text=text, link = link)

        else:
            response = "I did not understand that. Could you please repeat?"
            if request.data:
                # encode text for synthesizing speech
                response=response.replace("#"," ")
                # synthesize speech with rhasspy,audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)
                payload = {"html": render_template(
                    'index.html', result=response, text=text, link = link)}
                return payload

    else:
        return render_template('index.html', link = link)

@app.route('/audio_response/<variable>', methods=['POST', 'GET'])
def download(variable):

    return send_file(wav_response,as_attachment=True, download_name='audio.wav')

@app.route('/download')
def downloadFile ():
    filename = os.path.join(app.instance_path, "/Moody.pdf")
    return send_file(filename, as_attachment=True)

# executes when script is called -> starts the server, takes optional arguments like port number and debugging amount, see flask documentation
if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=5000,debug=True)
