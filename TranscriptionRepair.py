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

print("Parses a folder of xml files into a SRILM-readable text file, then uses that to fill transcription gaps in the original XML.")
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

    
lineIndex = 0

## LM BUILDING

LMname = path + "LM"

print("\n\nBuilding language model...")
os.system('ngram-count -sort -text ' + textName + ' -lm ' + LMname)
print("Done\n")

## LM APPLICATION AND CORRECTIONS

subs = string.letters + "ſ"

def generatePossibilities(word):
    if word.count('●') > 0 and word.count('●') < 3: #words with 3 or more unknown letters are very computationally expensive
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
textLines = text.read().split('\n')
text.close()

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
lineIndex = 0


for line in textLines:
    ind = textLines.index(line)
    words = line.split()
    for i in range(0, len(words)):
        word = words[i]
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
                if textWords.index(word + punc) < len(textWords) - 1:
                    bigram = guess + " " + textWords[textWords.index(word + punc) + 1]
                    for twoGram in twoGrams:
                        if twoGram.find(bigram) > -1:
                            bigramStrengths[float(twoGram.split("\t")[0])] = guess
                
                if textWords.index(word + punc) > 0:
                    bigram2 = textWords[textWords.index(word + punc) + -1] + " " + guess
                    for twoGram in twoGrams:
                        if twoGram.find(bigram2) > -1:
                            bigramStrengths[float(twoGram.split("\t")[0])] = guess
        
            print(word.decode('utf-8'), bigramStrengths)
        
            if len(bigramStrengths) > 0:
                maxStr = max(bigramStrengths.keys())
                words[i] = "<corrected>" + bigramStrengths[maxStr] + "</corrected>"
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
                    words[i] = "<corrected>" + onegramStrengths[maxStr] + "</corrected>"
                    corrected += 1
                else:
                    words[i] = word
                
            print words[i]
        outWords.append(word + punc)
    textLines[ind] = " ".join(words).decode('utf-8')

f = open(textName+"Corrected", 'w')
f.write(" ".join(outWords))
f.close()



print("\nCorrected " + str(corrected) + " out of " + str(unclear) + " words.\n")

## RECONSTRUCT XML

final = open('output.xml', 'w')
lineIndex = 0

for f in files:
    xmlFile = minidom.parse(path + "/" + f)
    lineList = xmlFile.getElementsByTagName('l')
    for s in range(0, len(lineList)):
        if len(lineList[s].childNodes) > 0:
            #print(s.childNodes[0].nodeValue)
            lineList[s].childNodes[0].nodeValue = textLines[lineIndex]
            lineIndex += 1
            
    final.write(xmlFile.toxml('utf-8'))

final.close()
        
final = open('output.xml', 'r')
output = final.read()
final.close()
output = output.replace('&lt;', '<').replace('&gt;', '>')
final = open('output.xml', 'w')
final.write(output)
final.close()
    
        