import pickle
import re
import random
import string
import json
from xml.etree import ElementTree as etree
from pycorenlp import StanfordCoreNLP
from xmljson import BadgerFish
from collections import OrderedDict

nlp = StanfordCoreNLP('http://localhost:9000')
vocab = pickle.load(open("voca","rb"))
revVocab = pickle.load(open("revVoca","rb"))

def convert(revVocab, words):

    if type(words) == str:
        words = words.strip().lower().split(' ')
    return [revVocab.get(w, 0) for w in words]

def revert(vocab, indices):
    return [vocab.get(i, 'X') for i in indices]




def is_ascii(s):
    return all(ord(c) < 128 for c in s)



if __name__ == '__main__':
    train = pickle.load(open("train","rb"))
    dev = pickle.load(open("dev","rb"))
    test = pickle.load(open("test", "rb"))
    trainList = []
    devList = []
    testList = []
    trainQT = open("trainQT_who", "wb")
    devQT = open("devQT_who", "wb")
    testQT = open("testQT_who", "wb")
    inFiles = {'train': train, 'dev': dev}
    outLists = {'train':trainList, 'dev': devList, 'test':testList}
    outFiles = {'train':trainQT, 'dev': devQT, 'test':testQT}

    aCount = 0
    tCount = 0
    qCount = 0
    termSet = set()
    aList = []
    qList = {}

    qTerms = ['who']
    #    qTerms = ['who', 'when', 'where', 'what']

    for file in inFiles.keys():

        for inLine in inFiles[file]:
            outLine = {}
            qWordList = revert(vocab, inLine["question"])
            if qWordList[0] in qTerms:
                print "qWordListB4\n"
                print qWordList
                print "\n"
                qWordList[0]  = "David"
                print "qWordListafter\n"
                print qWordList
                print "\n"
                outLine["question"] = convert(revVocab, qWordList)
                print "testConvert\n"
                print revert(outLine["question"])
                print "\n"
                outLine["question_id"] = inLine["question_id"]
                outLine["good"] = inLine["good"]
                outLine["bad"] = inLine["bad"]
                outLists[file].append(outLine)
        pickle.dump(outLists[file], outFiles[file])