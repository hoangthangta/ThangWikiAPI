import csv
import gc
import os
import subprocess
import requests
import xml.etree.ElementTree as ET
import json
import pandas as pd
import urllib

import sys
sys.setrecursionlimit(3000)
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), '')

import re
boundary = re.compile('^[0-9]$')
tag_re = re.compile(r'<[^>]+>')

import nltk
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

import spacy
from spacy import displacy
nlp = spacy.load('en_core_web_md')
nlp.add_pipe(nlp.create_pipe('sentencizer'), before='parser')
lemmatizer = nlp.vocab.morphology.lemmatizer

from datetime import *
from dateutil.easter import *
from dateutil.parser import *
from dateutil.relativedelta import *
from dateutil.rrule import *
from read_write_file import *


def remove_emojis(data):
    """
        remove emojis from Karim Omaya (stackoverflow.com)
    """
    emoj = re.compile('['
        u'\U0001F600-\U0001F64F'  # emoticons
        u'\U0001F300-\U0001F5FF'  # symbols & pictographs
        u'\U0001F680-\U0001F6FF'  # transport & map symbols
        u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
        u'\U00002500-\U00002BEF'  # chinese char
        u'\U00002702-\U000027B0'
        u'\U00002702-\U000027B0'
        u'\U000024C2-\U0001F251'
        u'\U0001f926-\U0001f937'
        u'\U00010000-\U0010ffff'
        u'\u2640-\u2642' 
        u'\u2600-\u2B55'
        u'\u200d'
        u'\u23cf'
        u'\u23e9'
        u'\u231a'
        u'\ufe0f'  # dingbats
        u'\u3030'
                      ']+', re.UNICODE)
    return re.sub(emoj, '', data)


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_data_by_sparql_query(query, data_format = 'json'):
    """
        get the data from Wikidata server by SPARQL queries
            query: string - a SPARQL query
            data_format: string - the format of return data
            return: list - a list of results
    """

    result_list = []
    link = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
    params = {
        'query': query,
        'format': data_format
        }
    
    response = requests.get(link, params)
    if (data_format == 'xml'):
        '''root = ET.fromstring(response.text) # convert to xml
        for x in root.find('./results/result'):
            try:
                name = remove_emojis(x.attrib['name'])
                value = remove_emojis(x.find('uri').value)
            except:
                pass'''
        pass
    
    elif(data_format == 'json'):
        root = json.loads(response.text)
        bindings = root['results']['bindings']
        for binding in bindings:
            result_list.append(binding)

    return result_list

def get_data_by_link(link, params = {}, data_format = 'xml'):
    """
        get data from a web link
            link: string - a web link
            return: string - web data
    """
    
    response = requests.get(link, params)
    if (data_format == 'xml'): root = ET.fromstring(response.text) # convert to xml
    return root

def search_wikipedia(term, limit = 1, language = 'en', data_format = 'json', key_len = 2):

    result_term = ''
    suggestion = False

    if (len(term) < key_len): return {'value': result_term, 'suggestion': suggestion}
    
    link = 'https://' +  language + '.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': term,
        'srlimit': limit,
        'srprop': 'size',
        'formatversion': 2,
        'format': data_format
        }

    response = requests.get(link, params)
    
    if (data_format == 'json'):
        root = json.loads(response.text)
        try:
            
            #total_hits = root['query']['searchinfo']['totalhits']
            #if (total_hits > 0):
            result_term = root['query']['searchinfo']['suggestion']
            suggestion = True
            if (term.strip().lower() == result_term.strip().lower()): result_term = term
            
        except:
            try:
                result_term = root['query']['search'][0]['title']
            except: pass
            pass

    return {'value': result_term, 'suggestion': suggestion}

def search_wikidata(term, search_type = 'property', limit = 50, data_format = 'xml'):

    result_list = []
    link = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbsearchentities',
        'language': 'en',
        'format': data_format,
        'type': search_type,
        'limit': limit,
        'search': term
        }
    
    response = requests.get(link, params)
    if (data_format == 'xml'):
        root = ET.fromstring(response.text) # convert to xml
        for x in root.find('./search'):
            try:
                wdid = remove_emojis(x.attrib['id'])
                title = remove_emojis(x.attrib['title'])
                label = remove_emojis(x.attrib['label'])
                object_type = ''

                if ('Property:' in title):
                    datatype = remove_emojis(x.attrib['datatype'])
                    object_type = 'property'
                else:
                    datatype = 'wikibase-item'
                    object_type = 'item'
                #text = remove_emojis(x.attrib['text'])
                if (wdid != ''):
                    result_list.append({'wikidata_id': wdid, 'title': title , 'label': label, 'datatype': datatype, 'object_type': object_type})
            except:
                pass
            
    return result_list


def get_data_by_wiki_title(title, data_format = 'xml', language = 'en', timeout = 30):
    """
        get xml data by title from English Wikipedia
            title: string - a Wikipedia's page title
            language: string - a syntax for a language
            return: string - xml data
    """
    
    link = 'https://' + language + '.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': data_format,
        'explaintext': True,
        'prop': 'extracts|revisions|pageprops|templates|categories',
        'rvprop': 'content',
        'rvslots': 'main',
        'titles': title,
        }
    response = requests.get(link, params, timeout = timeout)
    if (data_format == 'xml'): root = ET.fromstring(response.text) # convert to xml
    return root
    

def get_first_paragraph(title):
    link = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&titles=' + urllib.parse.quote(title)
    response = requests.get(link, timeout = 30) # 30s

    first_paragraph = ''
    #print('link: ', link)
    #print('response.text: ', response.text)
    try:
        data_dict = json.loads(response.text)
        data_dict = data_dict['query']['pages']
        key = next(iter(data_dict)) 
        first_paragraph = data_dict[key]['extract']
        
    except Exception as e:
        #print('Error --- get_first_paragraph: ', e)
        pass

    return first_paragraph


def get_triple(word, level = 2):

    #print('word: ', word)

    triple_list = []
    term_dict = get_wikidata_by_text(word)
    if not term_dict: return []
    
    instances = term_dict['instances']
    subclasses = term_dict['subclasses']
    parts = term_dict['parts']
            
    for i in instances: triple_list.append([term_dict['label'], 'instance_of', i[1]])
    for s in subclasses: triple_list.append([term_dict['label'], 'subclass_of', s[1]])
    for p in parts: triple_list.append([term_dict['label'], 'part_of', p[1]])

    # get property data
    triple_list += get_extend_triple(triple_list, instances, subclasses, parts, level)

    return triple_list

def get_extend_triple(triple_list, instances, subclasses, parts, level):

    if (level == 0):
        return triple_list
    
    # get property data
    id_list = [i[0] for i in instances]
    id_list += [s[0] for s in subclasses]
    id_list += [p[0] for p in parts]

    for item in id_list:
        term_dict = get_wikidata_by_wikidata_id(item)
        try: 
            instances = term_dict['instances']
            for i in instances: triple_list.append([term_dict['label'], 'instance_of', i[1]])
        except Exception as e:
            print('Error1 -- get_extend_triple: ', e)
            instances = {}
            pass

        try:
            subclasses = term_dict['subclasses']
            for s in subclasses: triple_list.append([term_dict['label'], 'subclass_of', s[1]])
        except Exception as e:
            print('Error2 -- get_extend_triple: ', e)
            subclasses = {}
            pass

        try:
            parts = term_dict['parts']
            for p in parts: triple_list.append([term_dict['label'], 'part_of', p[1]])
        except Exception as e:
            print('Error3 -- get_extend_triple: ', e)
            parts = {}
            pass

    level = level - 1
    #print(triple_list, instances, subclasses, parts, level)
    
    return get_extend_triple(triple_list, instances, subclasses, parts, level)
    

def get_wikidata_by_wikidata_id(wikidata_id):

    result_dict = {}

    try:
        wikidata_root = get_wikidata_root(wikidata_id)
        description = get_description(wikidata_root)
        #print('description: ', description)
        #print('wikidata_id: ', wikidata_id)
    
        if ('disambiguation page' in description.lower() or 'wiki' in description.lower()): return {}

        label = get_label(wikidata_root)
        claims = get_claims(wikidata_root, wikidata_id)
        instances = get_instance_of(claims)
        subclasses = get_subclass_of(claims)
        #parts = get_part_of(claims)
        aliases = get_alias(wikidata_root)

        result_dict['wikidata_id'] = wikidata_id
        result_dict['label'] = label
        result_dict['description'] = description
        result_dict['instances'] = instances
        result_dict['subclasses'] = subclasses
        result_dict['aliases'] = aliases

        # get the first paragraph & first sentence of Wikipedia
        sitelink = get_sitelink(wikidata_root)
        #wiki_root = get_xml_data_by_title(sitelink)
        first_paragraph = get_first_paragraph(sitelink)
        sents = sent_detector.tokenize(first_paragraph)

        #print('sents: ', sents)

        result_dict['first_paragraph'] = ' '.join(s for s in sents)
        result_dict['first_sentence'] = sents[0]
        
        
    except Exception as e:
        #print('Error --- get_wikidata_by_wikidata_id: ', e)
        pass
    
    return result_dict
    

def get_wikidata_by_text(title):

    result_dict = {}
    root = get_xml_data_by_title(title)
    
    wikidata_id = get_wikidata_id(root)
    if (wikidata_id == '' or wikidata_id == None): return {}

    wikidata_root = get_wikidata_root(wikidata_id)
    description = get_description(wikidata_root)
    if ('disambiguation page' in description): return {}

    label = get_label(wikidata_root)

    claims = get_claims(wikidata_root, wikidata_id)
    instances = get_instance_of(claims)
    subclasses = get_subclass_of(claims)
    parts = get_part_of(claims)

    result_dict['wikidata_id'] = wikidata_id
    result_dict['label'] = label
    result_dict['description'] = description
    result_dict['instances'] = instances
    result_dict['subclasses'] = subclasses
    result_dict['parts'] = parts
    
    return result_dict

def get_wikidata_root(wikidata_id):
    """
        get xml data by if from Wikidata
            wikidata_id: string - an identifier of an Wikidata item
            return: return: string - xml data
    """
    
    if (wikidata_id == None or wikidata_id == ''): return ''
    
    link = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbgetentities',
        'format': 'xml',
        'ids': wikidata_id,
        }
    
    root = get_data_by_link(link, params)
    if (root is None): return ''
    
    return root

def get_property_datatype(root):
    """
        get the datatype from xml data
            root: string - xml data
            return: string - a property datatype
    """
    
    try:
        for x in root.find('./entities'):
            value = remove_emojis(x.attrib['datatype'])
            if (value != ''): return value
    except: pass
    return ''               

def get_sitelink_title(root, wiki = 'enwiki'):
    """
        get a sitelink of a Wikipedia project from the Wikidata's xml data
            root: string - xml data of Wikidata
            wiki: string - a shortcut for a Wikipedia project
            return: string - a sitelink
    """

    try:
        for x in root.find('./entities/entity/sitelinks'):
            if (x.attrib['site'] == wiki):
                value = remove_emojis(x.attrib['title'])
                if (value != ''): return value
    except: pass
    return ''

def get_wikidata_id(root):
    """
        get an identifier of an Wikidata item
            root: string - xml data of Wikidata
            return: string - WikidataID
    """
    
    for node in root.find('./query/pages/page'):
        if (node.tag == 'pageprops'): return node.attrib['wikibase_item']
    return ''

def get_page_content(root):
    """
        get page content from xml data
            root: string - xml data
            return: list - a list of text
    """
    
    text_list = [x.text for x in root.iter('extract')]
    return text_list[0] # first page content only
    

def get_content_by_section(text): # not finish
    """
        split text into sections (level 2 and level 3)
            text: string - a given text
            return: dict - a dictionary
    """
    
    return

def get_sentence_list_baseline(text):
    """
        get sentence list from text
            text: string - a given text
            return: list - a list of sentences
    """
    
    text = text.replace(u'\xa0', u' ')
    text = text.replace(u'"', u'')

    sen_list = text.split('.')    
    sen_list = [x.strip() for x in sen_list if x.strip() != '']
    sen_list = [x + '.' for x in sen_list1]
    return sen_list
    
def get_sentence_list_by_sentencizer(text):
    """
        get sentence list from text by spaCy sentencizer
            text: string - a given text
            return: list - a list of sentences
    """
    
    text = text.replace(u'\xa0', u' ')
    # text = text.replace(u'"', u'')
 
    doc = nlp(text)
    sen_list = []
    for sent in doc.sents:
        sen_list.append(sent.text.strip())

    sen_list = [x.strip() for x in sen_list if x.strip() != '' and '==' not in x] 
    return sen_list

def extract_first_sentence(text):  # bad code

    count = 0
    first_sentence = ''
    for w in text:
        first_sentence += w

        if (w == '('): count += 1
        if (w == ')'): count -= 1

        if (w == '.'):        
            if (len(first_sentence.split()) > 10 and count == 0): break

        #print('----', first_sentence)

    return  first_sentence

def get_label_by_wikidata_id(wdid, data_format = 'xml'):
    """
        get label by a Wikidata indenfifier
            wikidataID: string - an indenfifier of an Wikidata item
            return: string - item label
    """
    
    link = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbgetentities',
        'format': data_format,
        'ids': wdid
        }
    
    root = get_data_by_link(link, params)           
    return get_label(root)


def get_label(root, language = 'en'):
    """
        get label from xml data
            root: string - xml data
            language: string - a language syntax
            return: string - label
    """
    
    try:
        for x in root.find('./entities/entity/labels'):
            if (language == 'en'):
                if (x.attrib['language'] == language + '-gb' or x.attrib['language'] == language):
                    value = remove_emojis(x.attrib['value'])
                    if (value != ''): return value
            else:
                if (x.attrib['language'] == language):
                    value = remove_emojis(x.attrib['value'])
                    if (value != ''): return value
    except:
        pass
    return ''

def get_description(root, language = 'en'):
    """
        get label from xml data
            root: string - xml data
            language: string - a language syntax
            return: string - description
    """

    try:
        for x in root.find('./entities/entity/descriptions'):
            if (language == 'en'):
                if (x.attrib['language'] == language + '-gb' or x.attrib['language'] == language):
                    value = remove_emojis(x.attrib['value'])
                    if (value != ''): return value
            else:
                if (x.attrib['language'] == language):
                    value = remove_emojis(x.attrib['value'])
                    if (value != ''): return value
    except:
        pass
    return ''  
       

def get_values_by_property(claim_list, property_name, language = 'en'):
    """
        get values of a given property
            claim_list: list - Wikidata claims
            property_name: string - a Wikidata property name
            return: list - a list of properties
    """
    
    result_list = []
    try:
        for c in claim_list:
            if (c[1][1] == property_name):
                k = c[1][3] # wdid
                root = get_wikidata_root(k)
                label = get_label(root, language)
                result_list.append([k, label])
    except: pass

    return result_list

def get_instance_of(claim_list, language = 'en'):
    """
        get instance of a Wikidata item from its claims
            claim_list: list - Wikidata claims
            return: list - a list of instances
    """
    
    result_list = []
    try:
        for c in claim_list:
            if (c[1][1] == 'P31'):
                k = c[1][3]
                root = get_wikidata_root(k)
                instance_name = get_label(root, language)
                result_list.append([k, instance_name])
    except: pass

    return result_list
    
def get_subclass_of(claim_list, language = 'en'):
    """
        get instance of a Wikidata item from its claims
            claim_list: list - Wikidata claims
            return: list - a list of instances
    """
    
    result_list = []
    try:
        for c in claim_list:
            if (c[1][1] == 'P279'):
                k = c[1][3]
                root = get_wikidata_root(k)
                instance_name = get_label(root, language)
                result_list.append([k, instance_name])
    except: pass

    return result_list

def get_part_of(claim_list, language = 'en'):
    """
        get parts of a Wikidata item from its claims
            claim_list: list - Wikidata claims
            return: list - a list of parts
    """
    
    result_list = []
    try:
        for c in claim_list:
            if (c[1][1] == 'P361'):
                k = c[1][3]
                root = get_wikidata_root(k)
                instance_name = get_label(root, language)
                result_list.append([k, instance_name])
    except: pass

    return result_list
    

def get_nationality(claim_list, language = 'en'):
    """
        get nationality of a Wikidata item from its claims
            claim_list: list - Wikidata claims
            return: list - a list of nationalities
    """
    
    result_list = []
    try:
        for c in claim_list:
            if (c[1][1] == 'P27'):
                k = c[1][3]
                root = get_wikidata_root(k)
                country_name = get_label(root, language)
                result_list.append([k, country_name])
    except: pass

    return result_list
	
def get_alias(root, language = 'en'):
    """
        get aliases of a Wikidata item from its claims
            root: string - xml data
            return: list - a list of aliases
    """
    
    aliases = []
    try:
        for x in root.find('./entities/entity/aliases'):
            
            if (language == 'en'):
                if (x.attrib['id'] == language + '-gb' or x.attrib['id'] == language):
                    for t in x:
                        value = remove_emojis(t.attrib['value'])
                        if (value != ''): aliases.append(value)
            else:
                if (x.attrib['id'] == language):
                    for t in x:
                        value = remove_emojis(t.attrib['value'])
                        if (value != ''): aliases.append(value)
    except: pass
    
    return aliases
        
# get claims (Wikidata's statements) of a Wiki page   
def get_claims(root, wikidataID):

    #print('root, wikidataID:', root, wikidataID)

    claim_list = [] # statement list

    if (root == '' or root is None):
        return claim_list

    if (wikidataID == '' or wikidataID is None):
        return claim_list

    s = wikidataID # s: subject (item identifier, wikidataID)
    p = ob = pt = pv = q = qt = qv = ''
    # p: predicate (property), ob: object (property value identifier)
    # pt: object type (property value type), pv: object value (property value)
    # q: qualifier, qt: qualifier type, qv: qualifier value

    # loop each predicate (property)
    for predicate in root.find('./entities/entity/claims'):        
        #print('************************')
        #print('Property: ', predicate.attrib['id'])
        p = remove_emojis(predicate.attrib['id']) # predicate (property)
        for claim in predicate.iter('claim'):
            pt = remove_emojis(claim[0].attrib['datatype']) # property type
            #print('+', pt)
            for obj in claim.find('mainsnak'):
                try:
                    try:
                        # obj.attrib['value'].encode('unicode-escape').decode('utf-8')
                        pv = remove_emojis(obj.attrib['value'])
                    except Exception as e:
                        #print('Error:', e)
                        pass
                    if (pv != ''):
                        continue
                    objdict = obj[0].attrib

                    if ('id' in objdict):
                        #print('--', objdict['id'])
                        ob = remove_emojis(objdict['id']) # qualifier
                    elif ('time' in objdict):
                        #print('--', objdict['time'])
                        pv = remove_emojis(objdict['time']) # time
                    elif ('amount' in objdict):
                        #print('--', objdict['amount'])
                        pv = remove_emojis(objdict['amount']) # amount
                    # capture other data types (globle coordinate, etc)
                    # ...
                    else:
                        pass
                        #print('--', 'empty')
                except Exception as e:
                    pass
                    #print('Error:', e) 
			
            # check the number of qualifiers
            qual_properties = [t for t in claim.findall('qualifiers/property')]
            if (len(qual_properties) == 0):
                if (pt != 'wikibase-item'):
                    r1 = [s, p, pt, pv]
                    claim_list.append(['r1', r1]) # WST-1 statement
                else:
                    r2 = [s, p, pt, ob]
                    claim_list.append(['r2', r2]) # WST-2 statement
            else:
                if (pv != ''):
                    r3 = [s, p, pt, pv] # WST3-a
                else:
                    r3 = [s, p, pt, ob] # WST3-b 
                try:
                    for x in claim.find('qualifiers'):
                        #print('----', x.attrib['id'], x.tag)
                        q = remove_emojis(x.attrib['id']) # qualifier identifier
                        qt = remove_emojis(x[0].attrib['datatype']) # qualifier data type
                        subr = [q, qt]
                        children = x.getchildren()
                        for y in children:
                            for z in y.find('datavalue'):
                                qv = '' # qualifier value
                                if ('id' in z.attrib):
                                    #print('--------', z.attrib['id'])
                                    qv = remove_emojis(z.attrib['id']) # qualifier value
                                elif ('time' in z.attrib):
                                    #print('--------', z.attrib['time'])
                                    qv = remove_emojis(z.attrib['time']) # value
                                elif ('amount' in z.attrib):
                                    #print('--------', z.attrib['amount'])
                                    qv = remove_emojis(z.attrib['amount']) # value
                                # capture other data types (globle coordinate, etc)
                                # ...   
                                else:
                                    #print('--------', 'empty')
                                    qv = '' # set to empty
                                if (qv != ''):
                                    subr.append(qv)
                                    r3.append(subr) # add a qualifier value
                                    qv = '' # set to empty for new iterator
                except Exception as e:
                    pass
                    #print('Error: ', e)
                
                if (len(r3) > 4):
                    claim_list.append(['r3', r3]) # WST-3 statement
                else:
                    if (pt != 'wikibase-item'):
                        claim_list.append(['r1', r3]) # WST-1 statement
                    else:
                        claim_list.append(['r2', r3]) # WST-2 statement
            ob = pv = '' # reset values (important)
        #print('************************')    

    '''for c in claim_list:
        print('-----------------')
        print(c)'''

    return claim_list     

def filter_claim_by_type(claim_list, claim_type = 'r1'):

    """
        filter claims by types
            claim_list: list - a list of claims
            claim_type: string - claim type (r1, r2, r3)
            return: list - a filtered claim lists
    """
    
    result_list = []
    for x in claim_list:
        if (x[0] == claim_type): result_list.append(x)
            
    return result_list     

def get_property_by_object_id(object_id, claim_list):
    """
        get properies by an object id
            object_id: string - an identifier of an object
            claims: list - a list of claims
            return: list - a property list
    """
    property_list = []
    for x in claim_list:
        if (x[1][2] == object_id):
            for y in range(4, len(x[1])):
                property_list.append(x[1][y])
    
    return property_list   

def get_hypernyms(values, results, level = 3, language = 'en'):
    """
        get Wikidata hypernyms by hypernym level (recursive)
            values: list - a given list
            results: list - a list of hypernyms
            level: int - the level of hypernym
            return: list - a list of hypernyms
    """

    if (level == 0 or len(values) == 0):
        results += values
        results = [list(x) for x in set(tuple(x) for x in results)] # keep unique values
        return results

    terms = []
    for v in values:
        try:
            root = get_wikidata_root(v[0])
            claim_list = get_claim(root, v[0])

            terms += get_values_by_property(claim_list, 'P31', language)
            terms += get_values_by_property(claim_list, 'P279', language)
        except: pass
        
    results += values
    results += terms
    results = [list(x) for x in set(tuple(x) for x in results)] # keep unique values

    terms = set(tuple(x) for x in terms)
    values = set(tuple(x) for x in values)
    terms = terms - values
    terms  = [list(x) for x in terms]

    return get_hypernyms(terms, results, level - 1, language)
    
'''# get wikidata item
def get_wikidata_item_by_name(item_name, file_name, depth):

    item_name = item_name.replace(' ','_') # format page name
    root = ''
    wikidata_id = ''
    
    try:
        root = get_xml_data_by_title(item_name)
        wikidata_id = get_wikidata_id(root)
    except Exception as e:
        #print('Error:', e)
        return []

    if (wikidata_id == ''):
        return []

    if (check_exist_in_item_list(wikidata_id) == True):
        return

    if (depth == 0):
        return []

    #print(wikidata_id)
    wikidata_root = get_wikidata_root(wikidata_id)
    xmlstr = ET.tostring(wikidata_root, encoding='unicode', method='xml')

    items = []
    items = match_wikidata_item(xmlstr)
    
    if ('Could not find an entity' in xmlstr or 'missing=""' in xmlstr):
        return

    label = description = ''
    alias = claims = []

    try:
        label = get_label(wikidata_root)
        description = get_description(wikidata_root)
        alias = get_alias(wikidata_root)
        claims = get_claims(wikidata_root, wikidata_id)
    except Exception as e:
        #print('Error:', e)
        return []
        
    write_to_text_file('item_id_list.txt', wikidata_id)
    write_wikidata_to_csv_file(file_name, wikidata_id, label, description, alias, claims)
	
    for i in items:
        get_wikidata_item_by_id(i, file_name, depth-1)

# get wikidata item
def get_wikidata_item_by_id(wikidata_id, file_name, depth):

    if (check_exist_in_item_list(wikidata_id) == True):
        return []

    if (depth == 0):
        return []

    wikidata_root = get_wikidata_root(wikidata_id)
    xmlstr = ET.tostring(wikidata_root, encoding='unicode', method='xml')

    items = []
    items = match_wikidata_item(xmlstr)
    
    if ('Could not find an entity' in xmlstr or 'missing=""' in xmlstr):
        return []

    label = description = ''
    alias = claims = []

    try:
        label = get_label(wikidata_root)
        description = get_description(wikidata_root)
        alias = get_alias(wikidata_root)
        claims = get_claims(wikidata_root, wikidata_id)
        
    except Exception as e:
        #print('Error:', e)
        return []

    write_to_text_file('item_id_list.txt', wikidata_id)
    write_wikidata_to_csv_file(file_name, wikidata_id, label, description, alias, claims)
    for i in items:
        get_wikidata_item_by_id(i, file_name, depth-1)'''

#.....................................................................
if __name__ == "__main__":
    print("Hello, this is Wiki Core library!")
    search_wikipedia("science")


