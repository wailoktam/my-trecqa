#!/usr/bin/env python
# coding: utf-8

import codecs
from pycorenlp import StanfordCoreNLP
from xml.etree import ElementTree as etree
import pickle
import re
import random

nlp = StanfordCoreNLP('http://localhost:9000')
data_path = u'./'
num_p = re.compile('<[0-9]*>')

lemmaSet = set()

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

def process(input):
    num = ''
    count = 0

    data = {}
    lemma_sent = []

    for line in codecs.open(input, 'r', 'utf-8'):
        
        if num_p.match(line) and u'¥t' not in line:
            num = int(line.replace('<','').replace('>','').strip())
            count = 1
            #print " ".join(lemma_sent)
            #print num
            if lemma_sent and num:
                data[num] = lemma_sent
            lemma_sent = []

        if count == 0:
            sent = str(" ".join(line.split(u'¥t')))
            lparseXML = etree.fromstring(lparse(sent))

            tokens = lparseXML.findall('.//token')
                
            for token in tokens:
                lemma = token.find(".//lemma").text
                lemma_sent.append(lemma)
                lemmaSet.add(lemma)
        
        count -= 1

    #print data

    return data

if __name__ == '__main__':
    train_q = process(data_path + 'train.question')
    test_q = process(data_path + 'test.question')
    dev_q = process(data_path + 'dev.question')

    train_a = process(data_path + 'train.answer')
    test_a = process(data_path + 'test.answer')
    dev_a = process(data_path + 'dev.answer')

    lem_num = 0
    lemmaDic = {}
    revlemmaDic = {}

    for term in lemmaSet:
        lem_num += 1
        lemmaDic[term] = lem_num
        revlemmaDic[lem_num] = term

    print '# of all voca : ' + str(len(lemmaDic.keys()))

    pickle.dump(lemmaDic, open('voca', 'w'))
    pickle.dump(revlemmaDic, open('revVoca', 'w'))

    ans_count = 0
    ans_list = []
    train_ans_dic = {}
    test_ans_dic = {}
    dev_ans_dic = {}

    for ans_id in train_a.keys():
        ans_count += 1
        sent = train_a[ans_id]
        new_sent = []
        temp_dic = {}
        for term in sent:
            new_sent.append(lemmaDic[term])
        temp_dic['id'] = ans_count
        temp_dic['text'] = new_sent
        train_ans_dic[ans_id] = ans_count

        ans_list.append(temp_dic)

    for ans_id in test_a.keys():
        ans_count += 1
        sent = test_a[ans_id]
        new_sent = []
        temp_dic = {}
        for term in sent:
            new_sent.append(lemmaDic[term])
        temp_dic['id'] = ans_count
        temp_dic['text'] = new_sent
        test_ans_dic[ans_id] = ans_count

        ans_list.append(temp_dic)

    for ans_id in dev_a.keys():
        ans_count += 1
        sent = dev_a[ans_id]
        new_sent = []
        temp_dic = {}
        for term in sent:
            new_sent.append(lemmaDic[term])
        temp_dic['id'] = ans_count
        temp_dic['text'] = new_sent
        dev_ans_dic[ans_id] = ans_count

        ans_list.append(temp_dic)

    print '# of all answers : ' + str(len(ans_list))

    pickle.dump(ans_list, open('answers', 'w'))

    train_list = []      

    for train_id in train_q.keys():
        temp = {}
        temp['question_id'] = train_id
        temp['good'] = train_ans_dic[train_id]
        new_sent = []
        for term in train_q[train_id]:
            new_sent.append(lemmaDic[term])
        temp['question'] = new_sent
        sample = train_ans_dic.keys()
        sample.remove(train_id)
        temp['bad'] = random.sample(sample, 20)
        train_list.append(temp)

    print '# of train questions : ' + str(len(train_list))
    pickle.dump(train_list, open('trains', 'w'))

    test_list = []

    for test_id in test_q.keys():
        temp = {}
        temp['question_id'] = test_id
        temp['good'] = test_ans_dic[test_id]
        new_sent = []
        for term in test_q[test_id]:
            new_sent.append(lemmaDic[term])
        temp['question'] = new_sent

        sample = test_ans_dic.keys()
        sample.remove(test_id)
        temp['bad'] = random.sample(sample, 20)

        test_list.append(temp)

    print '# of test questions : ' + str(len(test_list))
    pickle.dump(test_list, open('tests', 'w'))

    dev_list = []

    for dev_id in dev_q.keys():
        temp = {}
        temp['question_id'] = dev_id
        temp['good'] = dev_ans_dic[dev_id]

        new_sent = []
        for term in dev_q[dev_id]:
            new_sent.append(lemmaDic[term])
        temp['question'] = new_sent

        sample = dev_ans_dic.keys()
        sample.remove(dev_id)
        temp['bad'] = random.sample(sample, 20)

        dev_list.append(temp)

    print '# of dev questions : ' + str(len(dev_list))
    pickle.dump(dev_list, open('devs', 'w'))
