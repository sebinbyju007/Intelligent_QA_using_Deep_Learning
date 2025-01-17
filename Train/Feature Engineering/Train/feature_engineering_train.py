# -*- coding: utf-8 -*-
"""feature_train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11pHH0-1d33dwcmXBqJkSprDaM-YoOTUn
"""

!pip install distance
!pip install fuzzywuzzy

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import distance
import matplotlib.pyplot as plt
from subprocess import check_output
# %matplotlib inline
import plotly.offline as py
py.init_notebook_mode(connected=True)
import plotly.graph_objs as go
import plotly.tools as tls
import os
import gc

import re
from nltk.corpus import stopwords
import distance
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings("ignore")
import distance
from nltk.stem import PorterStemmer
from fuzzywuzzy import fuzz
#from sklearn.manifold import TSNE
from wordcloud import WordCloud, STOPWORDS
from os import path
from PIL import Image

df = pd.read_csv('train.csv.zip')
df.head(8)

df.info()

print( round(df['is_duplicate'].mean()*100, 2),"% duplicated question pairs.")
print(100- round(df['is_duplicate'].mean()*100, 2),"% non duplicated question pairs.")
df.groupby("is_duplicate")['id'].count().plot.bar()

df = df.fillna('')

if os.path.isfile('feature_tm.csv'):
  df = pd.read_csv('feature_tm.csv',encoding='latin-1')
else:


  def common_word(row):
      w1 = set(map(lambda word: word.lower().strip(), row.question1.split(" ")))
      w2 = set(map(lambda word: word.lower().strip(), row.question2.split(" ")))    
      return 1.0 * len(w1 & w2)

  def total_word(row):
      w1 = set(map(lambda word: word.lower().strip(), row.question1.split(" ")))
      w2 = set(map(lambda word: word.lower().strip(), row.question2.split(" ")))    
      return 1.0 * (len(w1) + len(w2))

  def word_share(row):
      w1 = set(map(lambda word: word.lower().strip(), row.question1.split(" ")))
      w2 = set(map(lambda word: word.lower().strip(), row.question2.split(" ")))    
      return 1.0 * len(w1 & w2)/(len(w1) + len(w2))

  def get_2_gram_share(row):
      q1_list = str(row.question1).lower().split()
      q2_list = str(row.question2).lower().split()
      q1_2_gram = set([i for i in zip(q1_list, q1_list[1:])])
      q2_2_gram = set([i for i in zip(q2_list, q2_list[1:])])
      shared_2_gram = q1_2_gram.intersection(q2_2_gram)
      if len(q1_2_gram) + len(q2_2_gram) == 0:
          R2gram = 0
      else:
          R2gram = len(shared_2_gram) / (len(q1_2_gram) + len(q2_2_gram))
      return R2gram

  df['ques1_len'] = df.question1.str.len()
  df['ques2_len'] = df.question2.str.len()
  df['len_diff'] = df.ques1_len - df.ques2_len
  
  df['q1_word_len'] = df.question1.apply(lambda row: len(row.split(" ")))
  df['q2_word_len'] = df.question2.apply(lambda row: len(row.split(" ")))
  df['words_diff'] = df.q1_word_len - df.q2_word_len
  
  df['q1_caps_count'] = df.question1.apply(lambda x:sum(1 for i in str(x) if i.isupper()))
  df['q2_caps_count'] = df.question2.apply(lambda x:sum(1 for i in str(x) if i.isupper()))
  df['caps_diff'] = df.q1_caps_count - df.q2_caps_count
  
  df['q1_char_len'] = df.question1.apply(lambda x: len(str(x).replace(' ', '')))
  df['q2_char_len'] = df.question2.apply(lambda x: len(str(x).replace(' ', '')))
  df['diff_char_len'] = df.q1_char_len - df.q2_char_len
  
  df['avg_word_len1'] = df.q1_char_len / df.q1_word_len
  df['avg_word_len2'] = df.q2_char_len / df.q2_word_len
  df['diff_avg_word'] = df.avg_word_len1 - df.avg_word_len2

  df['common_word'] = df.apply(common_word, axis=1)
  df['total_word'] = df.apply(total_word, axis=1)
  df['word_share'] = df.apply(word_share, axis=1)
  df['share_2_gram'] = df.apply(get_2_gram_share, axis=1) 

  df.to_csv('feature_tm.csv', index=False)

df.head()

df_new = df.head(1)

df_new

df_new = df_new.drop(['id',	'qid1',	'qid2',	'question1'	,'question2'	,'is_duplicate'	,'ques1_len',	'ques2_len','q1_word_len',	'q2_word_len','q1_caps_count',	'q2_caps_count','q1_char_len',	'q2_char_len'],axis=1)

df_new.plot.bar()

import nltk
nltk.download('stopwords')

SAFE_DIV = 0.0001 

from nltk.corpus import stopwords
STOP_WORDS = stopwords.words('english')

def preprocess(x):
    x = str(x).lower()
    x = x.replace(",000,000", "m").replace(",000", "k").replace("′", "'").replace("’", "'")\
                           .replace("won't", "will not").replace("cannot", "can not").replace("can't", "can not")\
                           .replace("n't", " not").replace("what's", "what is").replace("it's", "it is")\
                           .replace("'ve", " have").replace("i'm", "i am").replace("'re", " are")\
                           .replace("he's", "he is").replace("she's", "she is").replace("'s", " own")\
                           .replace("%", " percent ").replace("₹", " rupee ").replace("$", " dollar ")\
                           .replace("€", " euro ").replace("'ll", " will")
    x = re.sub(r"([0-9]+)000000", r"\1m", x)
    x = re.sub(r"([0-9]+)000", r"\1k", x)
    
    
    porter = PorterStemmer()
    pattern = re.compile('\W')
    
    if type(x) == type(''):
        x = re.sub(pattern, ' ', x)
    
    
    if type(x) == type(''):
        x = porter.stem(x)
        example1 = BeautifulSoup(x)
        x = example1.get_text()
               
    
    return x

from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import pickle
import gensim
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models.keyedvectors import KeyedVectors

glove2word2vec(glove_input_file="glove.840B.300d.txt", word2vec_output_file="glove_vectors.txt")
glove_model = KeyedVectors.load_word2vec_format("glove_vectors.txt", binary=False)

import pickle

with open('glove_model.pickle','wb') as handle:
  pickle.dump(glove_model,handle,protocol= pickle.HIGHEST_PROTOCOL )

from scipy.stats import skew, kurtosis
from scipy.spatial.distance import cosine, cityblock, canberra, euclidean, minkowski

def remove_stop(sentence):
    sentence  = str(sentence)
    if sentence == None:
        return ' '
    if sentence == np.nan:
        return ' '
    if sentence == 'NaN':
        return ' '
    z = [i for i in sentence.split() if i not in STOP_WORDS]
    return ' '.join(z)
  
def wmd(s1, s2, model):
  #WMD enables us to assess the “distance” between two documents in a meaningful
  #way even when they have no words in common.
  #It uses word2vec [4] vector embeddings of words. 
    
    s1 = str(s1)
    s2 = str(s2)
    s1 = s1.split()
    s2 = s2.split()
    return model.wmdistance(s1, s2)

def g2w2v(list_of_sent, model, d):
    sent_vectors = []
    for sentence in list_of_sent: 
        doc = [word for word in sentence if word in model.wv.vocab] 
        if doc:
            sent_vec = np.mean(model.wv[doc],axis=0) 
        else:
            sent_vec = np.zeros(d)
        sent_vectors.append(sent_vec)
    return sent_vectors

def get_distance_features(df):
    
    print("Extracting Distance Features..")
    
    df['question1'] = df.question1.apply(remove_stop)
    df['question2'] = df.question2.apply(remove_stop)
    df['word_mover_dist'] = df.apply(lambda x: wmd(x['question1'], x['question2'],glove_model), axis=1)
    
    print("- wmd done...")
    
    list_of_question1=[]
    for sentence in df.question1.values:
        list_of_question1.append(sentence.split())
    
    list_of_question2=[]
    for sentence in df.question2.values:
        list_of_question2.append(sentence.split())
    
    g2w2v_q1 = g2w2v(list_of_question1, glove_model, 300) # return the vector of each words in sentence
    g2w2v_q2 = g2w2v(list_of_question2, glove_model, 300)
    
    print("- embedding done...")
    
    df['cosine_dist'] = [cosine(q1, q2) for (q1, q2) in zip(g2w2v_q1,g2w2v_q2)]
    df['cityblock_dist'] = [cityblock(q1, q2) for (q1, q2) in zip(g2w2v_q1,g2w2v_q2)]
    df['canberra_dist'] = [canberra(q1, q2) for (q1, q2) in zip(g2w2v_q1,g2w2v_q2)]
    df['euclidean_dist'] = [euclidean(q1, q2) for (q1, q2) in zip(g2w2v_q1,g2w2v_q2)]
    df['minkowski_dist'] = [minkowski(q1, q2) for (q1, q2) in zip(g2w2v_q1,g2w2v_q2)]
    
    print('- spatial distance done')
    
    df.cosine_dist = df.cosine_dist.fillna(0)
    df.word_mover_dist = df.word_mover_dist.apply(lambda wmd: 30 if wmd == np.inf else wmd )
   
    return df

def get_token_features(q1, q2):
    token_features = [0.0]*10
    
    q1_tokens = q1.split()
    q2_tokens = q2.split()

    if len(q1_tokens) == 0 or len(q2_tokens) == 0:
        return token_features
    
    q1_words = set([word for word in q1_tokens if word not in STOP_WORDS])
    q2_words = set([word for word in q2_tokens if word not in STOP_WORDS])
    
    q1_stops = set([word for word in q1_tokens if word in STOP_WORDS])
    q2_stops = set([word for word in q2_tokens if word in STOP_WORDS])
    
    common_word_count = len(q1_words.intersection(q2_words))
    
    common_stop_count = len(q1_stops.intersection(q2_stops))
    
    common_token_count = len(set(q1_tokens).intersection(set(q2_tokens)))
    
    token_features[0] = common_word_count / (min(len(q1_words), len(q2_words)) + SAFE_DIV)
    token_features[1] = common_word_count / (max(len(q1_words), len(q2_words)) + SAFE_DIV)
    token_features[2] = common_stop_count / (min(len(q1_stops), len(q2_stops)) + SAFE_DIV)
    token_features[3] = common_stop_count / (max(len(q1_stops), len(q2_stops)) + SAFE_DIV)
    token_features[4] = common_token_count / (min(len(q1_tokens), len(q2_tokens)) + SAFE_DIV)
    token_features[5] = common_token_count / (max(len(q1_tokens), len(q2_tokens)) + SAFE_DIV)
    
    token_features[6] = int(q1_tokens[-1] == q2_tokens[-1])
    
    token_features[7] = int(q1_tokens[0] == q2_tokens[0])
    
    token_features[8] = abs(len(q1_tokens) - len(q2_tokens))
    
    token_features[9] = (len(q1_tokens) + len(q2_tokens))/2
    return token_features


def get_longest_substr_ratio(a, b):
    strs = list(distance.lcsubstrings(a, b))
    if len(strs) == 0:
        return 0
    else:
        return len(strs[0]) / (min(len(a), len(b)) + 1)

def extract_features(df):
    df["question1"] = df["question1"].fillna("").apply(preprocess)
    df["question2"] = df["question2"].fillna("").apply(preprocess)

    print("Extracting Token Features...")
    
    token_features = df.apply(lambda x: get_token_features(x["question1"], x["question2"]), axis=1)
    
    df["cwc_min"]       = list(map(lambda x: x[0], token_features))
    df["cwc_max"]       = list(map(lambda x: x[1], token_features))
    df["csc_min"]       = list(map(lambda x: x[2], token_features))
    df["csc_max"]       = list(map(lambda x: x[3], token_features))
    df["ctc_min"]       = list(map(lambda x: x[4], token_features))
    df["ctc_max"]       = list(map(lambda x: x[5], token_features))
    df["last_word_eq"]  = list(map(lambda x: x[6], token_features))
    df["first_word_eq"] = list(map(lambda x: x[7], token_features))
    df["abs_len_diff"]  = list(map(lambda x: x[8], token_features))
    df["mean_len"]      = list(map(lambda x: x[9], token_features))
   
    print("Extracting Fuzzy Features..")

    df["token_set_ratio"]       = df.apply(lambda x: fuzz.token_set_ratio(x["question1"], x["question2"]), axis=1)
    df["token_sort_ratio"]      = df.apply(lambda x: fuzz.token_sort_ratio(x["question1"], x["question2"]), axis=1)
    df["fuzz_ratio"]            = df.apply(lambda x: fuzz.QRatio(x["question1"], x["question2"]), axis=1)
    df["fuzz_partial_ratio"]    = df.apply(lambda x: fuzz.partial_ratio(x["question1"], x["question2"]), axis=1)
    df["longest_substr_ratio"]  = df.apply(lambda x: get_longest_substr_ratio(x["question1"], x["question2"]), axis=1)
    return df

if os.path.isfile('feature_nlp.csv'):
    df_nlp = pd.read_csv("feature_nlp.csv",encoding='latin-1')
else:
    print("Extracting features for train:")
    df = pd.read_csv("train.csv.zip")
    df = extract_features(df)
    df = get_distance_features(df)
    df = df.drop(['qid1','qid2','question1','question2','is_duplicate'], axis=1)
    df.to_csv("feature_nlp.csv", index=False)
df.head()

df_tm = pd.read_csv('feature_tm.csv')
df_nlp = pd.read_csv('feature_nlp.csv')
df_tm = df_tm.merge(df_nlp,on='id',how='left')
df_tm = df_tm.drop(['qid1',	'qid2',	'question1',	'question2',	'is_duplicate'],axis = 1)
df_tm.to_csv('feature_tm+nlp.csv',index=False)
df_tm.head()

