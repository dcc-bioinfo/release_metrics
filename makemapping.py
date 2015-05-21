import sys
import os
import re


#open the mapping file

mapping = open ("mapping.txt",'r')

#create our dictonary

namedict = dict()

for project in mapping:
    line = re.split(r'\t',project) #split project into tabs
    line[2] = line[2].rstrip("\n")
    line[2] = line[2].strip('\"')
    line[1] = line[1].strip('\"')
    namedict[line[0]] = line[1],line[2]
    print namedict[line[0]][1]


#read in all.data

table = open ("all_exist.data",'r')
tablenew = open ("all_exist_name.data",'w')

table.readline()

for s in table:
    line = re.split(r'\t',s) #split project into tabs
    projkey = line[0]

    #print country and name data
    tablenew.write (projkey+"\t"+namedict[projkey][0]+"\t"+namedict[projkey][1])
    for a in line:
        if a != projkey:
            tablenew.write ("\t"+a)

