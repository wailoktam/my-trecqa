#!/usr/bin/env python
# coding: utf-8

import pickle
import xml.etree.ElementTree as et
import sys
from pycorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP('http://localhost:9000')
dataPath = u'./'

datas = {}
answers = []
lemmaSet = set()
lemmaDic = {}
revLemmaDic = {}

def lparse(input):

    output = nlp.annotate(input, properties={
        'annotators': 'tokenize,ssplit,pos,lemma',
        'outputFormat': 'xml',
        'timeout': 30000})
    fixed = []
    for o in output:
        if all(ord(c) < 128 for c in o):
            fixed.append(o)
    return("".join(fixed))


def nlp_process(file_path):

    result = []
    
    xml = et.parse(file_path)
    tree = xml.getroot()
    
    for QApair in tree.findall('.//QApairs'):

        temp = {}

        if 'positive' not in list(QApair):
            continue

        for value in ['question', 'positive', 'negative']:

            sents = []

            for document in QApair.findall(value):

                sent = []

                raw_sent = document.text.split(u'¥n')[0].replace(u'¥t',' ')
                parse_result = et.fromstring(lparse(raw_sent))

                tokens = parse_result.findall('.//token')
                for token in tokens:
                    lemma = token.find(".//lemma").text
                    sent.append(lemma)
                    lemmaSet.add(lemma)

                sents.append(sent)

            temp[value] = sents

        result.append(temp)

    return result


def convert_sent(sent):
    new_sent = []
    for term in sent:
        new_sent.append(revLemmaDic[term])
    return new_sent


def process(nlped_data):
    num = 0
    resunt = []

    for document in nlped_data:
        num += 1
        temp = {}

        temp['question_id'] = num
        temp['question'] = convert_sent(document['question'][0])
        if len(document['question']) > 1:
            print 'question size is 2!'
            print document['question']
            sys.exit()

        good = []
        bad = []

        for value in ['positive', 'negative']:
            for sent in document[value]:
                ans = {}
                ans['id'] = len(answers) + 1
                ans['text'] = convert_sent(sent)
                answers.append(ans)

                if value == 'positive': 
                    good.append(ans['id'])
                else:
                    bad.append(ans['id'])

        temp['good'] = good
        temp['bad'] = bad
            
        result.append(temp)
        
    return result


if __name__ == '__main__':
    raws = {}
    raws['train'] = dataPath + 'train2393.cleanup.xml'
    raws['test'] = dataPath + 'test-less-than-40.manual-edit.xml'
    raws['dev'] = dataPath + 'dev-less-than-40.manual-edit.xml'

    nlped = {}

    for data_type in raws.keys():
        nlped[data_type] = nlp_process(raws[data_type])

    lem_num = 0

    for term in lemmaSet:
        lem_num += 1
        lemmaDic[lem_num] = term
        revLemmaDic[term] = lem_num

    print '# of all voca : ' + str(len(lemmaDic.keys()))

    pickle.dump(lemmaDic, open('voca', 'w'))
    pickle.dump(revlemmaDic, open('revVoca', 'w'))

    for data_type in nlped.keys():
        dump = process(nlped[data_type])
        print '# of all ' + data_type + ' : ' + str(len(dump))
        pickle.dump(dump, open(data_type, 'w'))

    print '# of all answers : ' + str(len(answers))
    pickle.dump(ans_list, open('answers', 'w'))






    
