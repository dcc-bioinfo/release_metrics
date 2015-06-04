from __future__ import division
import sys
import os
import parseForWGS
import gzip
#finds clinical data percentage for every project in raw data.
#INPUT: directory containing raw data 
#OUTPUT: % clinical metrics for each project. 1 file per project. Also 2 files containing % for all projects for dcc and PCAWG

directory = sys.argv[1]
filetype = sys.argv[2]

#open the directory to view the projects

allpercent = open ("all_clinical.txt",'w')
pallpercent = open ("pcawg_clinical.txt",'w')
projfile = open ("signedofflist.txt",'r')
projlist = projfile.readlines()
projlist = map (lambda s: s.strip(), projlist)

pcawgfields = open ("pcawgfields.txt",'r')
pcawgfields = pcawgfields.readlines()
pcawgfields = map (lambda s: s.strip(), pcawgfields)

#print header to summary files
allpercent.write ("filler\n")
pallpercent.write ("filler\n")

for filename in os.listdir(directory):
    currentproject = filename
    if currentproject not in projlist:
        continue

    allpercent.write (currentproject+"\t")
    pallpercent.write (currentproject+"\t")
    #open a file for this
    out = open (currentproject+"_clinical_percentages.txt",'w')
    filelist=[]
    #open this project folder
    if not os.path.isfile(filename) and not filename.startswith('.') and "TEST" not in filename:
        for files in os.listdir(directory+"/"+currentproject):
            if not files.startswith('.'):
                #check if file is .gz
                if filetype in files:
                    filelist.append(directory+"/"+currentproject+"/"+files) #add this file to our filelist
        if filelist == []:
            continue
        #run readALL
        parseForWGS.readAll(filelist,pcawgfields)
        #avg variables
        avgtotal =0
        avgpcawg =0
        total_fields = 0
        
        touselist =["donor","specimen","sample","therapy","family","exposure"]
        for a in [filetype]:
            avglist =parseForWGS.getClinicalPercentage(a,out,allpercent,pallpercent)
            avgtotal += avglist[0]
            avgpcawg += avglist[1]
            total_fields += avglist[2]

        parseForWGS.clearAll()
        #print avg, we are assuming total_fields entries. 
        out.write ("Average\t"+"{:.1%}".format(avgtotal/total_fields)+"\t")
        allpercent.write ("{:.1%}".format(avgtotal/total_fields))
        if avgpcawg != 0:
            out.write ("{:.1%}".format(avgpcawg/total_fields))
            pallpercent.write ("{:.1%}".format(avgpcawg/total_fields))
        else:
            out.write ("N/A")
            pallpercent.write ("N/A")
        out.close()
    allpercent.write ("\n")
    pallpercent.write ("\n")
  

allpercent.close()
pallpercent.close()
