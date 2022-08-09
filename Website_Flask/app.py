from urllib import response
from flask import Flask, render_template, request, send_file
from urllib.parse import quote
from network import synthesize, recognize, rasa_connector
import time
import os
import datetime

wav_question = "question.wav"
wav_response = "response.wav"

# create Flask instance
app = Flask(__name__)


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
            text = stt(wav_question,"vosk-model-small-en-us-0.15.zip")
            

        else:

            #  extract form data if there was any in the request
            text = str(request.form.get("question"))
            print(text)

        if text not in (None, '',"None"):
            
            print("The patient said: " + text)

            response = rasa_connector(text)

            print("Rasa answers: " +  response)

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
        return render_template('index.html')

@app.route('/audio_response/<variable>', methods=['POST', 'GET'])
def download(variable):
    print('audio.wav' + str(datetime.datetime.now()))
    return send_file(wav_response,as_attachment=True, download_name='audio.wav')

@app.route('/download')
def downloadFile ():
    filename = os.path.join(app.instance_path, "/Moody.pdf")
    return send_file(filename, as_attachment=True)

# executes when script is called -> starts the server, takes optional arguments like port number and debugging amount, see flask documentation
if __name__ == "__main__":
    app.run(debug=True)
