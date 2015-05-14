from __future__ import division
import sys
import os
import parseForWGS
import gzip
#finds clinical data percentage for every project in raw data.
#INPUT: directory containing raw data 
#OUTPUT: % clinical metrics for each project. 1 file per project. Also 2 files containing % for all projects for dcc and PCAWG

directory = sys.argv[1]

#open the directory to view the projects

allpercent = open ("all_clinical.txt",'w')
pallpercent = open ("pcawg_clinical.txt",'w')
#print header to summary files

allpercent.write ("filler\n")
pallpercent.write ("filler\n")

for filename in os.listdir(directory):
    currentproject = filename
    allpercent.write (currentproject+"\t")
    pallpercent.write (currentproject+"\t")
    #open a file for this
    out = open (currentproject+"_clinical_percentages.txt",'w')
    filelist=[]
    #open this project folder
    if not os.path.isfile(filename):
        for files in os.listdir(directory+"/"+currentproject):
            if not files.startswith('.'):
                #check if file is .gz
                filelist.append(directory+"/"+currentproject+"/"+files) #add this file to our filelist
        #run readALL
        parseForWGS.readAll(filelist)
        #avg variables
        avgtotal =0
        avgpcawg =0
        for a in ["donor","specimen","sample"]:
            avglist =parseForWGS.getClinicalPercentage(a,out,allpercent,pallpercent)
            avgtotal += avglist[0]
            avgpcawg += avglist[1]

        parseForWGS.clearAll()
        #print avg
        out.write ("Average\t"+"{:.1%}".format(avgtotal/50)+"\t")
        allpercent.write ("{:.1%}".format(avgtotal/50))
        if avgpcawg != 0:
            out.write ("{:.1%}".format(avgpcawg/50))
            pallpercent.write ("{:.1%}".format(avgpcawg/50))
        else:
            out.write ("N/A")
            pallpercent.write ("N/A")
        out.close()
    allpercent.write ("\n")
    pallpercent.write ("\n")
  

allpercent.close()
pallpercent.close()
