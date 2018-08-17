from keras.models import Model
from keras.layers import Input, LSTM, Dense, Embedding
import keras
from sklearn.cross_validation import KFold
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
import PyPDF2


def loadTxt(fp):
    with open(fp, "r") as infile:
        t = infile.read()
    return t


def loadPdf(fp):
    with open(fp, 'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        np = pdfReader.numPages
        texts = [pdfReader.getPage(p).extractText() for p in range(np)]
    return texts


def mkGroup(t):
    c = []
    for p in t.split("\n"):
        c.append(sum([x.split("?") for x in p.replace("?", "$$?").replace(
            ".", "^^.").replace("\n", "").split(". ")], []))
    p_p = []
    for p in c:
        s_p = []
        for s in p:
            s_p.append(s.replace("$$", " ? ")
                       .replace( "^^", " . ")
                       .replace("’’", ' " ')
                       .replace("‘‘", ' " ')
                       .replace(":", " : ")
                       .replace(";", " ; ")
                       .replace("'", " ' ")
                       .replace(",", " , ")
                       .replace("-", " - ")
                       .lower().split())
        p_p.append(s_p)
    return p_p


def dumbHigherMap(fn, itr):
    return map(lambda y: list(map(fn, y)), itr)

def shift(arr, num, fill_value=np.nan):
    if num >= 0:
        return np.concatenate((np.full((num, arr.shape[1], arr.shape[2]), fill_value), arr[:-num])).squeeze()
    else:
        return np.concatenate((arr[-num:], np.full((-num, arr.shape[1], arr.shape[2]), fill_value))).squeeze()

class DataGenerator(keras.utils.Sequence):
    'Generates data for Keras'

    def __init__(self, paragraphs=None, batch_size=6, shuffle=True, x_size=3, embeddingLookup=None, stopChar = None, startChar="~" ):
        'Initialization'
        self.batch_size = batch_size
        self.shuffle = shuffle
        # self.resample = resample
        self.x_size = x_size
        self.paragraphs = paragraphs
        self.stopchar = stopChar
        self.startchar = startChar
        self.embeddingLookup = embeddingLookup
        self.lookupEmbedding = {v:k for k,v in self.embeddingLookup.items()}
        self.embedding_vocab_size = len(embeddingLookup.keys())
        assert self.embedding_vocab_size is not None, "Must specify vocabulary size!"
        if not paragraphs:
            self.paragraphs = loadTxt("./data/2008 What should we do with our brain (C. Malabou) 2.txt").replace(
                "- ", "").split("Notes Introduction: Plasticity and Flexibility—For a Consciousness of the Brain ")[0]
            for footnote in range(20):
                self.paragraphs = self.paragraphs.replace(str(footnote), "")
            self.paragraphs = mkGroup(self.paragraphs)

        else:
            self.paragraphs = paragraphs
        if not self.stopchar: # FIXME: This is actually the decoder-target stopchar.  X does not have a stopchar, we just rely on the mask or end of array
            self.stopchar = np.zeros((1, self.embedding_vocab_size))
        else:
            raise NotImplementedError  # "stop char is set to zero vector"
        self.startchar = self.embeddingLookup[self.startchar]
        self.on_epoch_end()

    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.paragraphs) / self.batch_size))

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        paragraphs_temp = [self.paragraphs[k] for k in indexes]
        # Generate data
        [X,d ], y = self.__data_generation(paragraphs_temp)

        return [X, d], y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.arange(len(self.paragraphs))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, paragraphs_temp):
        def go(x):
            if x in self.embeddingLookup: 
                return self.embeddingLookup[x]
            else:
                return self.embeddingLookup['unknown']
        tokenized_para = list(map(lambda x: ( list(dumbHigherMap(go,x))), paragraphs_temp))
        y = tokenized_para
        X = [(np.array(x)[np.random.choice(len(x), self.x_size).tolist()]).tolist() for x in y] # Choose x_size sentences from each paragraph in y
        y = [[self.startchar,] + sum( x, []) for x in  y] # concat all sentences in each paragraph
        X = [sum(x, []) for x in  X] # concat all sentences in sampled
        y = keras.preprocessing.sequence.pad_sequences(
            y, value=0, padding='post')
        X = keras.preprocessing.sequence.pad_sequences(
            X, value=0, padding='post') # Pad
        d = shift(y.reshape(-1, len(tokenized_para), 1), 1, fill_value=0)
        X = X.reshape(-1, len(tokenized_para))
        if d.shape[0]> X.shape[0]: 
            diff = np.full((d.shape[0] - X.shape[0], X.shape[1]), 0)
            X = np.concatenate([X, diff], axis=0)
        elif d.shape[0] < X.shape[0]: # FIXME: Should not occur.
            diff = np.full((X.shape[0] - d.shape[0], X.shape[1]), 0)
            d = np.concatenate([d, diff], axis=0)
            try:
                y = np.concatenate([y.squeeze(), diff.T], axis=1)
            except Exception as e:
                print(y.shape)
                print(diff.shape)
                raise e

        y = np.apply_along_axis(lambda x:
                                keras.utils.to_categorical(
                                    x, num_classes=self.embedding_vocab_size), 1, y) # one-hot
        y = y.reshape((-1, len(tokenized_para), self.embedding_vocab_size))
        

        

        return [X, d], y # need to zero losses on padded targets.
