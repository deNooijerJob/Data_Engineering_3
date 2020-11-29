import os
import pandas as pd
from flask import Flask, json, request, Response
import numpy as np
import pickle
from keras import utils
from keras.models import load_model
from google.cloud import storage
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)
app.config["DEBUG"] = True

client = storage.Client()  # setup the storage
bucket = client.get_bucket(bucket_name)
blob_model = bucket.blob('models/model.h5')  # get the models from the bucket
blob_model.download_to_filename('downloaded_model.h5')  # download the model
model = load_model('downloaded_model.h5')  # load the model

blob_tokenizer = bucket.blob('models/tokenizer.pkl')
blob_tokenizer.download_to_filename('downloaded_tokenizer.pkl')
tokenizer = pickle.load(open("downloaded_tokenizer.pkl", 'rb'))


@app.route('precict', methods=['POST'])
def predict():
    requests = request.get_json()
    print(request)