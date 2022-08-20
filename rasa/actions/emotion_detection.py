import nltk
import numpy as np
import unicodedata
import string


nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger') 
nltk.download('omw-1.4')
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


# transform POS to wordnet scheme
def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return "a"
    elif treebank_tag.startswith('V'):
        return "v"
    elif treebank_tag.startswith('N'):
        return "n"
    elif treebank_tag.startswith('R'):
        return "r"
    else:
        return 'n'

# negation function for vad scores
def negate(score):

  for i in range(len(score)):
    difference = abs(score[i]-.5)
    if score[i] < .5:
      score[i] += difference*2
    else:
      score[i] -= difference*2
  return score

# Remove accents function
def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters or x == " ")

# Rule based ED
def emotion_detection_rule(input):

  # transform string into list
  input = input.split()

  stopwords = nltk.corpus.stopwords.words('english')
  stemmer = nltk.stem.PorterStemmer()
  lemmatizer = nltk.stem.WordNetLemmatizer()

  # remove accents and punctuation 
  input = [remove_accents(x) for x in input]

  # transform to lowercase
  input = [x.lower() for x in input]

  pos = nltk.pos_tag(input)

  for i in range(len(input)):
    input[i] = lemmatizer.lemmatize(input[i],get_wordnet_pos(pos[i][1]))

  score = [0,0,0]
  total = 0

  for i in range(len(input)):


    if input[i] in lex:
      
      if input[i-1] == ("not" or "never"):
        score = np.add(score,negate([float(i) for i in lex[input[i]]]))
      else:
        score = np.add(score,[float(i) for i in lex[input[i]]])
      total += 1

  if total > 0:
    score = [float(x)/total for x in score]

  return map_to_categories_vad(score,categories)

