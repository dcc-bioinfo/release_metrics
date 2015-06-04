from __future__ import division
import sys
import os
import re
import gzip
import bz2
#INPUT: directory containing raw data 
#OUTPUT: total number of whole genomes

idtostrat = {
        'WGS': "WGS",
        'WGA': "WGA",
        'WXS': "WXS",
        '1': "WGS",
        '2': "WGA",
        '3': "WXS",
        '4': "RNA-seq",
        '5': "miRNA-seq",
        '10': "AMPLICON",
        '16': "Bisulfite-seq",
        '30': "non-NGS",
        '0': "No-Data-temp",
        '-888': "No-Data-temp"
        }

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

def isInData (specimenid,data):
    foundpairs = []
    for pair in data:
        if specimenid == pair[0]:
            foundpairs.append(pair[1])
    return foundpairs


def checkAnalyzed(donorid,specimen,sample,data,table,donorids):
    global idtostrat
    #return all lines in specimen matching
    found = 0
    #matching = [s for s in specimen if donorid in s]
    matching = []
    foundseqstrats = []
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

            foundat = isInData(someid2[0],data)
            if foundat != []:
                #one donorid can count for a analysis type ONCE, but can count in multiple analysis
                for a in foundat:
                    seqstrat = idtostrat[a]
                    if seqstrat not in foundseqstrats:
                        foundseqstrats.append(seqstrat)
                        table[seqstrat] +=1
                    found = 1
    #check if this donor only got no data 
    if len(foundseqstrats) == 1 and "No-Data-temp" in foundseqstrats and donorid not in donorids:
        table["No-Data"] +=1
    return found


def trimData(data,group):
    #gets rid of everything put analyzed sample id and sequencing strategy
    newdata=[]
    for s in data:
       sampleid = re.split (r'\t',s)
     
       if group == "dna":
           newdata.append((sampleid[1],sampleid[10]))
       elif group == "rnaseq":
           newdata.append((sampleid[1],sampleid[9]))
       elif group == "mirnaseq":
           newdata.append((sampleid[1],sampleid[10]))
       elif group == "epigenome":
           newdata.append((sampleid[1],sampleid[6]))
       else:
           newdata.append((sampleid[1],'0'))
    return newdata

def main(go):

    donors = [] #list containing all donors
    specimen = [] #list containing all specimen file
    sample = [] #list containing all sample files
    data = [] #list containing metadata (everything with _m)

    #groups = ["dna","rnaseq","mirnaseq","epigenome","protein","arraybase"]
    groups = ["dna"]

    #groups = ["all"]

    directory = sys.argv[1]

    #open the directory to view the projects

    total = 0

    sys.stdout.write ("project_key\tWGS\tWGA\tWXS\tRNA-Seq\tmiRNA-seq\tBisulfite-Seq\tNon-NGS\tAMPLICION\tNo_Data")


    for filename in os.listdir(directory):

        idtostrat = {
            "WGS":0,
            "WGA":0,
            "WXS":0,
            "RNA-seq":0,
            "miRNA-seq":0,
            "AMPLICON":0,
            "Bisulfite-seq":0,
            "non-NGS":0,
            "No-Data-temp":0,
            "No-Data":0
        }


        sys.stdout.flush()
        sys.stdout.write("\n")
        sys.stdout.write(filename+"\t")

        donorids = []

        for group in groups:

            if group == "dna":
                flist = ["ssm_m","stsm_m","cnsm_m","jcn_m"]
            elif group == "rnaseq":
                flist = ["exp_seq_m"]
            elif group == "mirnaseq":
                flist = ["mirna_seq_m"]
            elif group == "epigenome":
                flist = ["meth_seq_m"]
            elif group == "protein":
                #no sequencing strategy
                flist = ["pexp_m"]
            elif group == "arraybase":
                #no sequencing strategy
                flist = ["exp_array_m","meth_array_m"]

            metafilelist=[]
            donorfilelist=[]
            specimenfilelist=[]
            samplefilelist=[]

            #flip this on to do calculate all donors
            #flist = ["_m"]
            #then skip rest

            #open this project folder
            if "TEST" in filename:
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

            for line in donors[1:]:
                someid = re.split(r'\t',line)
                #get the donor_id from the line
                potential_id = someid[0]
                if checkAnalyzed(potential_id,specimen,sample,data,idtostrat,donorids) == 1:
                    donorids.append(someid[0])
                    #sys.stdout.write someid[0]

            total += len(donorids)


            print "donorids:"+str(len(donorids))
        
        #print out the info for this project
        sys.stdout.write (str(idtostrat["WGS"])+"\t")
        sys.stdout.write (str(idtostrat["WGA"])+"\t")
        sys.stdout.write (str(idtostrat["WXS"])+"\t")
        sys.stdout.write (str(idtostrat["RNA-seq"])+"\t")
        sys.stdout.write (str(idtostrat["miRNA-seq"])+"\t")
        sys.stdout.write (str(idtostrat["Bisulfite-seq"])+"\t")
        sys.stdout.write (str(idtostrat["non-NGS"])+"\t")
        sys.stdout.write (str(idtostrat["AMPLICON"])+"\t")
        sys.stdout.write (str(idtostrat["No-Data"])+"\t")
        
                            
#need to run "main" on every file group
main("guu")
#main("rnaseq")
#main("epigenome")
#main("protein")
#main("arraybase")
