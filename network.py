import websockets
import wave
import requests
import json
import asyncio
from vosk import Model, KaldiRecognizer, SetLogLevel


SetLogLevel(0)


def stt(wav_path,model_path):
    
    # if not os.path.exists("model"):
    #     print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    #     exit (1)

    wf = wave.open(wav_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print ("Audio file must be WAV format mono PCM.")
        exit (1)

    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    # rec.SetPartialWords(True)
    text = ""
    
    while True:
        data = wf.readframes(4000000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            text += json.loads(rec.Result())["text"]
        else:
            print(rec.PartialResult())
            text += json.loads(rec.PartialResult())["partial"]
            

    print(text)
    
    return text

def recognize(wav_question):
    return asyncio.run(recognize_websocket(wav_question))


async def recognize_websocket(wav_question):

    uri = 'ws://localhost:2700'

    async with websockets.connect(uri) as websocket:

        wf = wave.open(wav_question, "rb")
        await websocket.send('{ "config" : { "sample_rate" : %d } }' % (wf.getframerate()))
        buffer_size = int(wf.getframerate() * 0.2)  # 0.2 seconds of audio
        
        result = ""
        
        while True:
            data = wf.readframes(buffer_size)

            if len(data) == 0:
                break

            await websocket.send(data)
            result = (await websocket.recv())
            # print(result)
            # print(type(result))


        await websocket.send('{"eof" : 1}')
        try:    
            result = json.loads(result)["text"]
        except :
            result = json.loads(result)["partial"]
            
        # print(result)
        # print(type(result))
        return (result)


def synthesize(text, wav_response):

        # thorsten voice 
    # url = "http://localhost:5002/api/tts?voice=de-de%2Fthorsten-glow_tts&text=" + text + "&vocoder=hifi_gan%2Funiversal_large&denoiserStrength=0.005&noiseScale=0.333&lengthScale=0.85"
      
    #   kerstin voice
    # url = "http://localhost:5002/api/tts?voice=de-de%2Fkerstin-glow_tts&text="+text+"&vocoder=hifi_gan%2Funiversal_large&denoiserStrength=0.002&noiseScale=0.667&lengthScale=0.85&ssml=false"
    
    # english harvard voice
    # url = "http://localhost:5002/api/tts?voice=en-us%2Fharvard-glow_tts&text= "+text+"&vocoder=hifi_gan%2Funiversal_large&denoiserStrength=0.002&noiseScale=0.667&lengthScale=0.85&ssml=false"
    
     # english cmu_eey voice
    url = "http://localhost:5002/api/tts?voice=en-us/cmu_eey-glow_tts&text= "+text+"&vocoder=hifi_gan%2Fvctk_small&denoiserStrength=0.002&noiseScale=1&lengthScale=1&ssml=false"
    
    audio = requests.get(url).content

    with open(wav_response, mode="wb") as f:
        # write as wav, to bring in the right format for python
        f.write(audio)

#   prepare header and payload as JSON, send it to the RASA connector through the webhook (RASA Server needs to be running on port 5005) and receive the response)
def rasa_connector(text):

    payload = json.dumps({"sender": "Rasa", "message": text})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.request(
        "POST",   url="http://localhost:5005/webhooks/rest/webhook", headers=headers, data=payload).json()

    resp = ""

    #   append all responses with "text" into one string (todo: handle images, other kind of data)
    for i in range(len(response)):
        try:
            resp += response[i]['text'] + "  "
        except:
            continue
        
    return resp
