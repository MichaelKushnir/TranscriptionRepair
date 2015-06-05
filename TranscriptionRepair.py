# -*- coding: utf-8 -*-
"""
Created on Thu Jun 04 17:35:30 2015

@author: Misha Kushnir
"""

#from subprocess import call
from xml.dom import minidom
import os
import string
import loadLM

## XML PARSING

print("Parse a folder of xml files into a SRILM-readable text file.")
path = input("Enter folder name: ")

files = os.listdir(path)
#print files
textName = path + 'Parsed'

#use different files for building LM and analysis - for some reason, ngram-counts crashes on '\n'
text = open(textName, 'w')
test = open('testText', 'w')

for f in files:
    if f[-4:] == '.xml':
        print("Parsing xml file " + str(files.index(f) + 1) + " out of " + str(len(files)))
        xmlFile = minidom.parse(path + "/" + f)
        lineList = xmlFile.getElementsByTagName('l')
        for s in lineList:
            if len(s.childNodes) > 0:
                #print(s.childNodes[0].nodeValue)
                text.write((s.childNodes[0].nodeValue+' ').encode('utf-8'))
                test.write(s.childNodes[0].nodeValue.encode('utf-8'))
                test.write('\n')
            
text.close()
test.close()

## LM BUILDING

LMname = path + "LM"

print("\n\nBuilding language model...")
os.system('ngram-count -sort -text ' + textName + ' -lm ' + LMname)
print("Done\n")

## LM APPLICATION AND CORRECTIONS

subs = string.letters + "ſ"

def generatePossibilities(word):
    if word.find('●') > -1:
        ind = word.decode('utf-8').find('●'.decode('utf-8'))
        possibilities = []
        for letter in subs.decode('utf-8'):
            temp = list(word.decode('utf-8'))
            temp[ind] = letter
            temp = "".join(temp).encode('utf-8')
            for i in generatePossibilities(temp):
                possibilities.append(i)
                
        return possibilities
    else:
        return [word]
    

text = open('testText', 'r')
textWords = text.read().split()
text.close()

#for some reason, the exact same code only worked in a separate module.
LMlines = loadLM.readTestLM()
LM = "".join(LMlines)
twoInd = LMlines.index('\\2-grams:\n')
threeInd = LMlines.index('\\3-grams:\n')
oneGrams = LMlines[7:twoInd]
twoGrams = LMlines[twoInd:threeInd]
threeGrams = LMlines[threeInd:]

outWords = []

unclear = 0
corrected = 0

for word in textWords:
    #Strip punctuation, save in punc to reappend at end
    punc = ""
    if word[-1] in string.punctuation:
        punc = word[-1]
        word = word[0:-1]
        
    poss = generatePossibilities(word)
    bigramStrengths = {}
    if len(poss) > 1:
        unclear += 1
        #use 1-grams to prune possibilities
        for guess in poss:
            if LM.find(guess) == -1:
                poss.remove(guess)
                
        for guess in poss: #check 2-grams
            bigram = guess + " " + textWords[textWords.index(word + punc) + 1]
            for twoGram in twoGrams:
                if twoGram.find(bigram) > -1:
                    bigramStrengths[float(twoGram.split("\t")[0])] = guess
        
        print(word.decode('utf-8'), bigramStrengths)
        
        if len(bigramStrengths) > 0:
            maxStr = max(bigramStrengths.keys())
            word = bigramStrengths[maxStr]
            corrected += 1
        else: #check 1-gram frequencies
            onegramStrengths = {}
            for guess in poss:
                for oneGram in oneGrams:
                    if oneGram.find(guess) > -1:
                        onegramStrengths[float(oneGram.split("\t")[0])] = guess
                            
            if len(onegramStrengths) > 0:
                print(onegramStrengths)
                maxStr = max(onegramStrengths.keys())
                word = onegramStrengths[maxStr]
                corrected += 1
            else:
                word = word
                
        print word
    outWords.append(word + punc)


f = open(textName+"Corrected", 'w')
f.write(" ".join(outWords))
f.close()

print("\nCorrected " + str(corrected) + " out of " + str(unclear) + " words.\n")

## RECONSTRUCT XML

