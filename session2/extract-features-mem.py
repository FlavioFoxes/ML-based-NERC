#! /usr/bin/python3

import math
import sys
import re
from os import listdir

from xml.dom.minidom import parse
from nltk.tokenize import word_tokenize


   
## --------- tokenize sentence ----------- 
## -- Tokenize sentence, returning tokens and span offsets

def tokenize(txt):
    offset = 0
    tks = []
    ## word_tokenize splits words, taking into account punctuations, numbers, etc.
    for t in word_tokenize(txt):
        ## keep track of the position where each token should appear, and
        ## store that information with the token
        offset = txt.find(t, offset)
        tks.append((t, offset, offset+len(t)-1))
        offset += len(t)

    ## tks is a list of triples (word,start,end)
    return tks

## --------- get tag ----------- 
##  Find out whether given token is marked as part of an entity in the XML

def get_tag(token, spans) :
   (form,start,end) = token
   for (spanS,spanE,spanT) in spans :
      if start==spanS and end<=spanE : return "B-"+spanT
      elif start>=spanS and end<=spanE : return "I-"+spanT

   return "O"
 
## --------- Feature extractor ----------- 
## -- Extract features for each token in given sentence

def count_connected_letters(txt, letters):
   low = txt.lower()
   connectedLetters = 0
   for i in range(len(low)-1): 
      if low[i] in letters and low[i+1] in letters: 
         connectedLetters += 1
   return connectedLetters

def first_connected_letters(txt, letters):
   low = txt.lower()
   for i in range(len(low)-1): 
      if low[i] in letters and low[i+1] in letters: 
         return str(low[i]+low[i+1])
   return "NaN"

def count_commas_lines(txt): 
   retVal = 0
   for i in range(len(txt)):
      if txt[i] == ',' or txt[i] == '-':
         retVal += 1
   return retVal

def digits_and_sign(txt):
   digits = ['0','1','2','3','4','5','6','7','8','9']
   signs = [',','-']
   retVal = 0
   for i in range(len(txt)-1):
      if (txt[i] in signs and txt[i+1] in digits) or (txt[i] in digits and txt[i+1] in signs):
         retVal += 1
   return retVal

def count_upper(txt):
   retVal = 0
   for i in range(len(txt)):
      if (txt[i].isupper()):
         retVal += 1
   return retVal

def extract_features(tokens) :
    result = []
    consonants = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z']
    vowels = ['a','e','i','o','u']
    for k in range(0,len(tokens)):
        t = tokens[k][0]
        tokenFeatures = [];

        # for each token, generate list of features and add it to the result
        ### CURRENT TOKEN ###
        for i in range(0,len(t)-2):
           tokenFeatures.append("seq3="+t[i]+t[i+1]+t[i+2])
        tokenFeatures.append("reverse="+t[len(t)::-1])
        tokenFeatures.append("form="+t)   
        tokenFeatures.append("numLetters="+str(len(t)))
        tokenFeatures.append("pref4="+t[:4])     
        tokenFeatures.append("suf3="+t[-3:])
   
        ### PREVIOUS TOKEN ### 
        if k>0 :
           tPrev = tokens[k-1][0]
           for i in range(0,len(tPrev)-2):
              tokenFeatures.append("seq3Prev="+tPrev[i]+tPrev[i+1]+tPrev[i+2])

           tokenFeatures.append("reversePrev="+tPrev[len(t)::-1])
           tokenFeatures.append("formPrev="+tPrev)
           tokenFeatures.append("numLettersPrev="+str(len(tPrev)))
           tokenFeatures.append("pref4Prev="+tPrev[:4])
           tokenFeatures.append("suf3Prev="+tPrev[-3:])
        else :
           tokenFeatures.append("BoS")      # Bos: Beginning of Sentence

        ### NEXT TOKEN ###
        if k<len(tokens)-1 :
            tNext = tokens[k+1][0]
            for i in range(0,len(tNext)-2):
               tokenFeatures.append("seq3Next="+tNext[i]+tNext[i+1]+tNext[i+2])
            tokenFeatures.append("reverseNext="+tNext[len(t)::-1])
            tokenFeatures.append("formNext="+tNext)
            tokenFeatures.append("numLettersNext="+str(len(tNext)))
            tokenFeatures.append("pref4Next="+tNext[:4])
            tokenFeatures.append("suf3Next="+tNext[-3:])
        else:
            tokenFeatures.append("EoS") # EoS: End of Sentence
        result.append(tokenFeatures)
    return result


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  baseline-NER.py target-dir
## --
## -- Extracts Drug NE from all XML files in target-dir, and writes
## -- them in the output format requested by the evalution programs.
## --


# directory with files to process
datadir = sys.argv[1]

# process each file in directory
for f in listdir(datadir) :
   
   # parse XML file, obtaining a DOM tree
   tree = parse(datadir+"/"+f)
   
   # process each sentence in the file
   sentences = tree.getElementsByTagName("sentence")
   for s in sentences :
      sid = s.attributes["id"].value   # get sentence id
      spans = []
      stext = s.attributes["text"].value   # get sentence text
      entities = s.getElementsByTagName("entity")
      for e in entities :
         # for discontinuous entities, we only get the first span
         # (will not work, but there are few of them)
         (start,end) = e.attributes["charOffset"].value.split(";")[0].split("-")
         typ =  e.attributes["type"].value
         spans.append((int(start),int(end),typ))
         

      # convert the sentence to a list of tokens
      tokens = tokenize(stext)
      # extract sentence features
      features = extract_features(tokens)

      # print features in format expected by crfsuite trainer
      for i in range (0,len(tokens)) :
         # see if the token is part of an entity
         tag = get_tag(tokens[i], spans) 
         print (sid, tokens[i][0], tokens[i][1], tokens[i][2], tag, "\t".join(features[i]), sep='\t')

      # blank line to separate sentences
      print()