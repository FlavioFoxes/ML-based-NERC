#! /usr/bin/python3

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
   # PIPPO
   # for each token, generate list of features and add it to the result
   ### CURRENT TOKEN ###

      tokenFeatures.append("form="+t)   
      tokenFeatures.append("numLetters="+str(len(t)))
      #tokenFeatures.append("numVowels="+str(vcount))
      tokenFeatures.append("pref4="+t[:4])     
      tokenFeatures.append("suf3="+t[-3:])
      # tokenFeatures.append("Suf4Pref3=" + tPrev[-4:] + t[:3])

      # NIKO
      tokenFeatures.append("begfin="+t[:2]+t[-2:]) 
      tokenFeatures.append("skip="+t[0:len(t)-1:2])
      tokenFeatures.append("connCons="+str(count_connected_letters(t,consonants)))
      tokenFeatures.append("firstConnCons="+first_connected_letters(t,consonants))
      # tokenFeatures.append("connVowels="+str(count_connected_letters(t,vowels)))
      # tokenFeatures.append("firstConnVowels="+first_connected_letters(t,vowels)) VOWELS NOT THAT USEFUL
      tokenFeatures.append("numSigns="+str(digits_and_sign(t))) # -> not so good 
      tokenFeatures.append("upperCaseCount="+str(count_upper(t)))
      if len(t) % 2 == 0:
         mid = int(len(t)/2)
         tokenFeatures.append("central="+t[mid-1:mid])
      else:
         mid = int(math.floor(len(t)/2))
         tokenFeatures.append("central="+t[mid:mid+1])
      tokenFeatures.append("lmr="+t[0]+t[mid]+t[len(t)-1])   

      if k > 0:   # for the features that consider the previous token to extract the feature at the actual index
         tPrev = tokens[k-1][0]
         tokenFeatures.append("mid4="+tPrev[-2:]+t[:2])
         tokenFeatures.append("lastFirst="+tPrev[-1:]+t[0])
      else: 
         tokenFeatures.append("mid4=##"+t[:2])
         tokenFeatures.append("lastFirst=#"+t[0])

      if k < len(tokens) - 1: # for the features that consider the next token to excract the feature at the actual index
         tNext = tokens[k+1][0]
         tokenFeatures.append("firstFollowing="+t[:2]+tNext[:2])
      else: 
         tokenFeatures.append("firstFollowing="+t[:2]+"##")
   
      ### PREVIOUS TOKEN ### 

      if k>0 :
         tPrev = tokens[k-1][0]
         tokenFeatures.append("formPrev="+tPrev)
         tokenFeatures.append("numLettersPrev="+str(len(tPrev)))
         # good
         tokenFeatures.append("pref4Prev="+tPrev[:4])
         tokenFeatures.append("suf3Prev="+tPrev[-3:])
         
      # NIKO
         tokenFeatures.append("begFinPrev="+tPrev[:2]+tPrev[-2:])
         tokenFeatures.append("skipPrev="+tPrev[0:len(tPrev)-1:2])
         tokenFeatures.append("connConsPrev="+str(count_connected_letters(tPrev,consonants)))
         tokenFeatures.append("firstConnConsPrev="+ first_connected_letters(tPrev,consonants))
         # tokenFeatures.append("connVowelsPrev="+str(count_connected_letters(tPrev, vowels)))
         # tokenFeatures.append("firstConnVowelsPrev="+ first_connected_letters(tPrev,vowels)) 
         tokenFeatures.append("numSignsPrev="+str(digits_and_sign(tPrev))) 
         tokenFeatures.append("upperCaseCountPrev="+str(tPrev))
         if len(tPrev) % 2 == 0:
            mid = int(len(tPrev)/2)
            tokenFeatures.append("centralPrev="+tPrev[mid-1:mid])
         else:
            mid = int(math.floor(len(tPrev)/2))
            tokenFeatures.append("centralPrev="+tPrev[mid:mid+1])
         tokenFeatures.append("lmrPrev="+tPrev[0]+tPrev[mid]+tPrev[len(tPrev)-1])
         tokenFeatures.append("firstFollowingPrev="+tPrev[:2]+t[:2])
      else :
         tokenFeatures.append("BoS")      # Bos: Beginning of Sentence

 
      if k>1 :
         tPrev = tokens[k-1][0]
         tPrev2 = tokens[k-2][0]
         # good
         tokenFeatures.append("mid4Prev="+tPrev2[-2:]+tPrev[:2])
         tokenFeatures.append("lastFirstPrev="+tPrev2[-1:]+tPrev[0])
         #tokenFeatures.append("="+tPrevPrev[-3:])

   #      if re.search('[0-9]', tPrev) is not None:
   #         tokenFeatures.append("numberIsPresentPrev")
   #   
      else :
         tokenFeatures.append("BoS")      # Bos: Beginning of Sentence

      ### NEXT TOKEN ###

      if k<len(tokens)-1 :
         tNext = tokens[k+1][0]
         tokenFeatures.append("formNext="+tNext)
         tokenFeatures.append("numLettersNext="+str(len(tNext)))
         tokenFeatures.append("pref4Next="+tNext[:4])
         tokenFeatures.append("suf3Next="+tNext[-3:])
         tokenFeatures.append("lastFirstNext=" + t[-1:] + tNext[0])
         tokenFeatures.append("Suf4Pref3Next=" + t[-4:] + tNext[:3])

         # NIKO
         tokenFeatures.append("skipNext="+tNext[0:len(tNext)-1:2])
         tokenFeatures.append("begFinNext="+tNext[:2]+tNext[-2:])
         tokenFeatures.append("mid4Next="+t[-2:]+tNext[:2])
         tokenFeatures.append("connConsNext="+str(count_connected_letters(tNext,consonants)))
         tokenFeatures.append("firstConnConsNext="+first_connected_letters(tNext,consonants))
         # tokenFeatures.append("connVowelsNext="+str(count_connected_letters(tNext,vowels)))
         # tokenFeatures.append("firstConnVowelsNext="+first_connected_letters(tNext,vowels)) 
         tokenFeatures.append("numSignsNext="+str(digits_and_sign(tNext)))
         tokenFeatures.append("upperCaseCountNext="+str(count_upper(tNext)))
         if len(tNext) % 2 == 0:
            mid = int(len(tNext)/2)
            tokenFeatures.append("centralNext="+tNext[mid-1:mid])
         else:
            mid = int(math.floor(len(tNext)/2))
            tokenFeatures.append("centralNext="+tNext[mid:mid+1])
         tokenFeatures.append("lmrNext="+tNext[0]+tNext[mid]+tNext[len(tNext)-1])
      else:
         tokenFeatures.append("EoS")      # EoS: End of Sentence
      
      if k < len(tokens) - 2: 
         tNext = tokens[k+1][0]
         tNext2 = tokens[k+2][0]
         tokenFeatures.append("firstFollowingNext="+tNext[:2]+tNext2[:2])
      else: tokenFeatures.append("EoS")

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