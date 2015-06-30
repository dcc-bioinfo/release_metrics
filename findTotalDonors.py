from __future__ import division
import sys
import os
import re
import parseForWGS
import gzip
import bz2
#INPUT: directory containing raw data 
#OUTPUT: total number of whole genomes

def readFiles (filenames):
    #reads the found files and mashes them into a big list
    biglist = []
    for f in filenames:
        if ".gz" in f:
            lines = gzip.open (f,"r")
        elif ".bz2" in f:
            lines = bz2.BZ2File(f)
        else:
            lines = open (f,"r")
        lines = lines.readlines()
        biglist.extend(lines)
    return biglist

def common_elements(lista,listb):
    return list(set(lista).intersection(listb))

def checkAnalyzed(donorid,specimen,sample,data):
    #return all lines in specimen matching
    found = 0
    #matching = [s for s in specimen if donorid in s]
    matching = []
    for s in specimen:
        s = re.split (r'\t',s)
        if donorid == s[0]:
            matching.append(s[1])
    for a in matching:
        #get the specimenid 
        someid = a
        matching2 = [x for x in sample if someid in x]
        for g in matching2:
            someid2 = re.split (r'\t',g)
            if "analyzed_sample" in someid2[0]:
                continue
            if (someid2[0] in data):
                found = 1

    return found


def trimData(data,group):
    #gets rid of everything put analyzed sample id
    newdata=[]
    for s in data:
        sampleid = re.split (r'\t',s)
        if group == "dna":
            #we care about the sequencing strategy here (for DNA)
            if sampleid[10] == "3" or sampleid[10] == "1" or sampleid[10] == "2" or sampleid[10] == "WGA" or sampleid[10] == "WGS" or sampleid[10] == "WXS":
               newdata.append(sampleid[1])
        else:
           newdata.append(sampleid[1])
    return newdata

def main(go):

    donors = [] #list containing all donors
    specimen = [] #list containing all specimen file
    sample = [] #list containing all sample files
    data = [] #list containing metadata (everything with _m)

    #open file that contains commitment data
    #commitfile = open(sys.argv[2],'r')
    #commitlines = commitfile.readlines()

    groups = ["dna","rnaseq","arraybase","epigenome","protein"]

    #groups = ["all"]

    directory = sys.argv[1]

    anchorfilename = sys.argv[2]
    
    anchorfile = open(anchorfilename,'r')
    anchorlines = anchorfile.readlines()

    #open the directory to view the projects
    total = 0


    for filename in os.listdir(directory):
        sys.stdout.flush()
        sys.stdout.write("\n")
        for group in groups:

            if group == "dna":
                flist = ["ssm_m","stsm_m","cnsm_m","jcn_m"]
            elif group == "rnaseq":
                flist = ["mirna_seq_m","exp_seq_m","exp_m","mirna_m"]
            elif group == "epigenome":
                flist = ["meth_seq_m","meth_array_m"]
            elif group == "protein":
                #no sequencing strategy
                flist = ["pexp_m"]
            elif group == "arraybase":
                #no sequencing strategy
                flist = ["exp_array_m"]

            metafilelist=[]
            donorfilelist=[]
            specimenfilelist=[]
            samplefilelist=[]

            #flip this on to do calculate all donors
            #flist = ["_m"]
            #then skip rest

            #open this project folder
            if "TEST" in filename or "migration" in filename:
                continue
            if not os.path.isfile(filename):
                for files in os.listdir(directory+"/"+filename):
                    if not files.startswith('.') and ".bak" not in files:
                        if "donor" in files:
                            if "pancancer" not in files:
                                donorfilelist.append(directory+"/"+filename+"/"+files)
                        elif "specimen" in files:
                            specimenfilelist.append(directory+"/"+filename+"/"+files)
                        elif "sample" in files:
                            samplefilelist.append(directory+"/"+filename+"/"+files)
                        else:
                            for target in flist:
                                if target in files:
                                    metafilelist.append(directory+"/"+filename+"/"+files) 

            donors = readFiles (donorfilelist)
            specimen= readFiles (specimenfilelist)
            sample = readFiles (samplefilelist)
            data = readFiles (metafilelist)

            data = trimData(data,group)

            donorids = []

            for line in donors[1:]:
                someid = re.split(r'\t',line)
                #get the donor_id from the line
                potential_id = someid[0]
                if potential_id not in donorids:
                    if checkAnalyzed(potential_id,specimen,sample,data) == 1:
                        donorids.append(someid[0])
                        #sys.stdout.write someid[0]

            total += len(donorids)

            #find the commitment number for this project
            matching = [x for x in anchorlines if filename in x]
            if matching != []:
                matchsplit = matching[0].rsplit('\t')
                if matchsplit[4] != "\n":
                    anchor = int(matchsplit[4])
                else:
                    anchor = 1
            else:
                anchor = 1

            if group == "dna":
                # find the "goal" number, offset everything by that 
                wholegenomes = donorids
                sys.stdout.write (filename+"\t")
                if anchor != 1:
                    multiplier = len(wholegenomes)/anchor
                    if multiplier > 1:
                        multiplier = 1
                else:
                    multiplier = 1
                sys.stdout.write (str(100*multiplier))
                #sys.stdout.write (str(len(wholegenomes)))
            else:
                if wholegenomes != []:
                    sys.stdout.write ("\t"+"{:.1%}".format(len(common_elements(donorids,wholegenomes))/len(wholegenomes)*multiplier))
                else:
                    sys.stdout.write("\t0")
    #sys.stdout.write (str(total))

#need to run "main" on every file group
main("guu")
#main("rnaseq")
#main("epigenome")
#main("protein")
#main("arraybase")
