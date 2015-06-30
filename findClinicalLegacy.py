from __future__ import division
import sys
import re
import os
import gzip
#finds clinical data percentage for every project in raw data.
#INPUT: directory containing raw data 
#OUTPUT: % clinical metrics for each project. 1 file per project. Also 2 files containing % for all projects for dcc and PCAWG

def getClinicalPercentage(afile,logfile):
    print afile
    #Determines clinical percentages for ONE tab delimited file
    filelines = gzip.open (afile,'r')

    filelines = filelines.readlines()

    header = filelines[0]
    header = header.rstrip('\n')
    header = re.split(r'\t', header)
    
    headcount = [0]*len(header)
    totaldonors = 0
    avgtotal = 0

    #go through the rest of the lines for the file
    for s in filelines[1:]:
        s.rstrip('\n')
        totaldonors+=1
        index =0

        columns = re.split(r'\t', s)

        for c in columns:
            c = c.rstrip('\n')
            if c != "" and c!= "-777" and c!="-888" and "unknown" not in c and c!= " ":
                headcount[index]+=1
            index+=1
    print headcount 
    count=0
    for field in header:

        logfile.write(field+"\t"+str(headcount[count])+"/"+str(totaldonors)+"\n")
        avgtotal += headcount[count]/totaldonors
        count+=1
    

    print avgtotal,"//",len(headcount)
    return [avgtotal,len(headcount)]
    


def main():
    directory = sys.argv[1]
    #since only determining PCAWG donors requires several files together, this list is reserved for when we need it

    #open the directory to view the projects

    allpercent = open ("all_clinical.txt",'w')

    inclist = ["clinical","sample"] # list of "non-clinical" legacy files to ignore

    #we print header to the summary for now since we don't know what they contain yet
    allpercent.write ("filler\n")

    for filename in os.listdir(directory):
        currentproject = filename

        allpercent.write (currentproject+"\t")

        print currentproject,
        #open a file for this
        out = open (currentproject+"_clinical_percentages.txt",'w')
        out.write("field_name\tcompletion\n")
        filelist=[]
        #open this project folder
        if not os.path.isfile(filename) and not filename.startswith('.') and "TEST" not in filename and "README" not in filename:
            for files in os.listdir(directory+"/"+currentproject):
                if not files.startswith('.') and "no_detect" not in files and "README" not in files:
                    for e in inclist: 
                        if e in files:
                            filelist.append(directory+"/"+currentproject+"/"+files) #add this file to our filelist
            if filelist == []:
              allpercent.write ("\n")
              continue
            #run readALL
            #avg variables
            avgtotal =0
            total_fields = 0
            
            for a in filelist:
                avglist = getClinicalPercentage(a,out)
                avgtotal += avglist[0]
                total_fields += avglist[1]

            #print avg, we are assuming total_fields entries. 
            print avgtotal
            print total_fields
            out.write ("Average\t"+"{:.1%}".format(avgtotal/total_fields)+"\t")
            allpercent.write ("{:.1%}".format(avgtotal/total_fields))
            out.close()
        allpercent.write ("\n")
      

    allpercent.close()

main()
