from __future__ import division
import sys
import re
import os
import gzip
#finds clinical data percentage for every project in raw data.
#INPUT: directory containing raw data 
#OUTPUT: % clinical metrics for each project. 1 file per project. Also 2 files containing % for all projects for dcc and PCAWG

def analyze(filelist,cout,release):
    # find the list of sampleIDs first
    for name in filelist:
        if "sample" in name or "clinical" in name:
            if "gz" in name:
                filelines = gzip.open (name,'r')
            else:
                print name," is not a gz"
                continue
            filelines = filelines.readlines()
            header = filelines[0]
            header = header.rstrip('\n')

            headersplit = header.rsplit('\t')

            #release 1-2
            if "donor_id" in headersplit:
                donorid_index = headersplit.index("donor_id")   
                sampleid_index = headersplit.index("sample_id")   
            elif "Donor ID" in headersplit and "Sample ID" in headersplit:
                donorid_index = headersplit.index("Donor ID")   
                sampleid_index = headersplit.index("Sample ID")   

            donortosample = dict()

            for line in filelines[1:]:
                line = line.rsplit('\t')
                podonor = line[donorid_index]
                posample = line[sampleid_index]
                if podonor in donortosample:
                    donortosample[podonor].append(posample)
                else:
                    donortosample[podonor] = [posample]

            dnacount = 0 
            methcount = 0 
            expcount = 0 
            mirnacount = 0
            for donor in donortosample:
               found = False
               dnacounted = False
               for sampleid in donortosample[donor]:
                   # go through the analysis files and see if anything matches
                    #failsafe incase there is NO sampleID 
                    if sampleid == "":
                        continue
                    for otherfiles in filelist:
                        if "sample" not in otherfiles and "clinical" not in otherfiles:
                            # assume DNA if there isnt a sequencing strategy
                            if "gz" in otherfiles:
                                filelines = gzip.open (name,'r')
                            else:
                                print name," is not a gz"
                                continue
                            
                            filelines = filelines.readlines()
                            # try to find sequencing strategy in the header
                            eheader = filelines[0]
                            headersplit = eheader.rsplit('\t')
                            if "strategy" in headersplit:
                                pass
                            for line in filelines:
                                if sampleid in line:
                                    found = True
                                    if "meth" in otherfiles:
                                        methcount +=1
                                    elif "exp" in otherfiles:
                                        expcount+=1
                                    elif "mirna" in otherfiles:
                                        mirnacount +=1
                                    else:
                                        if not dnacounted:
                                            dnacount +=1
                                            dnacounted = True
                                    break
                    if found:
                        break
           
            cout.write("Release "+str(release)+": "+str(dnacount)+"\t"+str(expcount)+"\t"+str(methcount)+"\t"+str(mirnacount)+"\t"+str(len(donortosample))+"\n")
           # print "Analysis: DNA",dnacount,"//",len(donortosample)
           # print "Analysis: exp",expcount,"//",len(donortosample)
           #  print "Analysis: meth",methcount,"//",len(donortosample)
           #  print "Analysis: mirna",mirnacount,"//",len(donortosample)

def getClinicalPercentage(afile,logfile):
    #Determines clinical percentages for ONE tab delimited file
    if "gz" in afile:
        filelines = gzip.open (afile,'r')
    else: 
         print "Skipping ",afile," since it's not a gz"

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
    release = 1 
    for dirs in os.listdir(directory):
        print release
        if not os.path.isfile(dirs):
            #open the directory to view the projects
            for filename in os.listdir(directory+"/"+dirs):
                currentproject = filename
                cout =open (currentproject+"_legacy_analyzed",'a')
                #open a file for this
                filelist=[]
                #open this project folder
                if not os.path.isfile(filename) and not filename.startswith('.') and "TEST" not in filename and "README" not in filename:
                    for files in os.listdir(directory+"/"+dirs+"/"+currentproject):
                        if not files.startswith('.') and "no_detect" not in files and "README" not in files:
                                filelist.append(directory+"/"+dirs+"/"+currentproject+"/"+files) #add this file to our filelist
                    if filelist == []:
                      continue

                    avgtotal =0
                    total_fields = 0
                    
                    analyze(filelist,cout,release)

                    #print avg, we are assuming total_fields entries. 
                    cout.close()
	release +=1

main()
