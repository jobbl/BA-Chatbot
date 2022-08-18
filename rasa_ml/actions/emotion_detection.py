import tensorflow_hub as hub
import tensorflow as tf
import tensorflow_text as text
import numpy as np


classifier_model_vad = tf.keras.models.load_model("model.h5",custom_objects={'KerasLayer':hub.KerasLayer})

def emotion_detection_ml(text):

    score = classifier_model_vad(tf.constant([text])).numpy()[0]
    return map_to_categories_vad(score,categories)
# reloaded_model = tf.saved_model.load("actions/model")

categories = {"empty":[0,0,0,0,0,0,0],"threatened":[0,0,0,0,0,0,0],"tranquil":[0,0,0,0,0,0,0],"excited":[0,0,0,0,0,0,0],"rooted":[0,0,0,0,0,0,0]}

def map_to_categories_vad(vad_score,categories):
  vad_categories = {}
  differences = {}
  for category in categories:
    vad_categories[category] = lex[category]
  for category in vad_categories.keys():
    differences[category] = np.absolute(np.subtract(vad_categories[category],vad_score))
    mean = 0
    for x in differences[category]:
      mean += x
    mean = mean/len(differences[category])
    differences[category] = mean
  return (min(differences, key=differences.get))

# create NRC-VAD Lexicon
lexicon_path = "NRC-VAD-Lexicon.txt"
lex = {}

with open(lexicon_path) as f:
  for line in f:
    words = line.split()
    try:
      lex[words[0]] = [float(words[1]),float(words[2]),float(words[3])]
    except:
      continue

