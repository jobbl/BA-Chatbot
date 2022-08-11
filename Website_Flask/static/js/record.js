//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var recorder; 						//WebAudioRecorder object
var input; 							//MediaStreamAudioSourceNode  we'll be recording
var encodingType; 					//holds selected encoding for resulting audio (file)
var encodeAfterRecord = true;       // when to encode

var msg = new SpeechSynthesisUtterance();
var voices = window.speechSynthesis.getVoices();
msg.voice = voices[10]; 
msg.volume = 1; // From 0 to 1
msg.rate = 1; // From 0.1 to 10
msg.pitch = 1; // From 0 to 2
msg.lang = 'en';

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //new audio context to help us record
var audio;

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var textForm = document.getElementById("textForm");
var loader = document.getElementById("loader");
var result = document.getElementById("result");


//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
changeToAudio.addEventListener("click", toAudio);
changeToText.addEventListener("click", toText);

function toAudio(){
	changeToText.style.display = "block";
	recordButton.style.display = "block";
	textForm.style.display = "none";
	changeToAudio.style.display = "none";
}

function toText(){
	changeToAudio.style.display = "block";
	recordButton.style.display = "none";
	textForm.style.display = "block";
	changeToText.style.display = "none";
}

function startRecording() {
	stopButton.style.display = "block";
	recordButton.style.display = "none";

	console.log("startRecording() called");

	/*
		Simple constraints object, for more advanced features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/
    
    var constraints = { audio: true, video:false }

    /*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {

		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device

		*/
		audioContext = new AudioContext();

		//assign to gumStream for later use
		gumStream = stream;
		
		/* use the stream */
		input = audioContext.createMediaStreamSource(stream);
		
		//stop the input from playing back through the speakers
		//input.connect(audioContext.destination)

		//get the encoding 
		encodingType = "wav";


		recorder = new WebAudioRecorder(input, {
		  workerDir: "static/js/", // must end with slash
		  encoding: encodingType,
		  numChannels:1, //2 is the default, mp3 encoding supports only 2
		  onEncoderLoading: function(recorder, encoding) {
		    // show "loading encoder..." display
		  },
		  onEncoderLoaded: function(recorder, encoding) {
		    // hide "loading encoder..." display
		  }
		});

		recorder.onComplete = function(recorder, blob) { 

			const formData = new FormData();
			formData.append("audio", blob, "test.wav");
			
			// fetch("/", {method: "POST", body: formData});
			fetch("/", {method: "POST", body:blob}).then(response => response.json()).then((response) => {
				
				return response.html;
			}).then((html) => {
				console.log("here");
				var parser = new DOMParser();
				var doc = parser.parseFromString(html, "text/html");
				// document.getElementById("text").innerHTML = doc.getElementById("text").innerHTML;

				// download wav file from server
				audio = new Audio("/audio_response/" + new Date().getTime());
				audio.play();

				document.getElementById("result").innerHTML = doc.getElementById("result").innerHTML;
				loader.style.display = "none";
                recordButton.style.display = "block";
				result.style.display = "block";

			});
			console.log("data sent");
		}

		recorder.setOptions({
		  timeLimit:120,
		  encodeAfterRecord:encodeAfterRecord,
	      ogg: {quality: 0.5},
	      mp3: {bitRate: 160}
	    });

		//start the recording process
		recorder.startRecording();


	}).catch(function(err) {


	});

}

function stopRecording() {
	loader.style.display = "block";
	result.style.display = "none";
	stopButton.style.display = "none";
	
	console.log("stopRecording() called");
	
	//stop microphone access
	gumStream.getAudioTracks()[0].stop();
	
	
	//tell the recorder to finish the recording (stop recording + encode the recorded audio)
	recorder.finishRecording();
	console.log("finishRecording() finished");
	

}

