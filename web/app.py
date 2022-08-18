from urllib import response
from flask import Flask, render_template, request, send_file
from urllib.parse import quote
from network import synthesize, recognize, rasa_connector, stt
import time
import os

wav_question = "question.wav"
wav_response = "response.wav"

intro = "Welcome! You have found your way to an experiment about an emotion understanding therapy bot. At least thats the aim ^^. \n First, The bot will guide you through a little conversation of about 5 minutes. At the end it will ask you to follow a link to a short survey, which also takes about 5 minutes. Everything is totally anonymous. The things you say during the session are not saved, and the survey is anonymous. \n When you are ready, make sure you are not muted and then press on the \"Record\" Button. The browser will ask you for microphone permissions, if have not given them already. When you are done speaking, the bot will take a while to process and then answer you. Have fun!   "

# create Flask instance
app = Flask(__name__)

@app.route('/intro')
def intro():
    return render_template('intro.html')


# Whenever there is a request from the client to this url, run the following code
@app.route('/', methods=['POST', 'GET'])
def extract():
    
    if request.method == "POST":
    
        response = ""

        # if client recorded audio, there will be data
        if request.data:
        
            print("Received audio data with the size of " + str(request.content_length/1000) + "kb")

            with open(wav_question, mode="bw") as f:

                # write as wav, to bring in the right format for python
                f.write(request.data)

            # text = recognize(wav_question)
            text = stt(wav_question,"vosk-model-small-en-us-0.15")
            print("text:",text)

        else:

            #  extract form data if there was any in the request
            text = str(request.form.get("question"))
            print(text)

        if text not in (None, '',"None"):
            
            print("The patient said: " + text)

            response = rasa_connector(text)[0]
            print( "rule:",rasa_connector(text)[1])
            print( type(rasa_connector(text)[1]))

            # if rasa_connector(text)[1] is not None:
            #     response += rasa_connector(text)[1]

            print("Rasa answers: " +  response)

            if request.data:
            
                # encode teyt for synthesizing speech
                response=response.replace("#"," ")
                
                # audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)

                
                payload = {"html": render_template(
                    'index.html', result=response, text=text)}
                
                return payload

        else:
            
            response = "I did not understand that. Could you please repeat?"
            if request.data:
        
            # encode teyt for synthesizing speech
                response=response.replace("#"," ")
                
                # audio will be downloaded at /audio_response, see record.js
                synthesize(response, wav_response)

                
                payload = {"html": render_template(
                    'index.html', result=response, text=text)}
                
                return payload

        # render template with resp and the original user text (could be used for chat visualization)
            return render_template('index.html', result=response, text=text)
        
        return render_template('index.html', result=response, text=text)
    
    else:
        return render_template('index.html',intro = intro)

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
