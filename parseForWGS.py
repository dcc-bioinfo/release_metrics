#Findss the number of WGS based on a few files
from __future__ import division #needed to cacluate floats from two ints
import sys
import re
import subprocess #call terminal commands
import os #os functions (remove file)
import unittest #probably needed eventually
import gzip #read gzip
import bz2 #read bz2

#NAUGHTY NAUGHTY global variables
#these are lists containing lines of donor, specimen and sample files
donorfile =[]
specimenfile =[]
samplefile =[]

#new files in R19
therapyfile =[]
exposurefile =[]
familyfile =[]


def checkExistURL (command): 
    #checks if a curl url exists before attempting to download, so we don't flood people with 404 messages
    FNULL=open(os.devnull)
    process  = subprocess.Popen(command.split(),stdout=FNULL,stderr=subprocess.STDOUT)
    process.communicate
    process.wait()
    return process.returncode

def common_elements(lista,listb):
    return list(set(lista).intersection(listb))


def gunzipFiles (filename):
    #gunzips a file. Whether the file exists is NOT checked
    command = "gunzip -df "+filename+".gz" #zip will fail if there is already a file with same name
    process  = subprocess.Popen(command.split())
    process.communicate
    process.wait()

def deleteFiles (filelist):
    #get rid of files
    for dfile in filelist:
        try:
            os.remove (dfile)
        except:
            pass
    #ignore exception, file may not be there in first place

def addUniq (lista, listb): 
    #add door list b into list a, but only keep unique entries
    for donor in listb:
        if donor not in lista:
            lista.append(donor)

    return lista;


def clearAll ():
    #clears our globals for next project
    global donorfile
    global specimenfile
    global samplefile
    global therapyfile
    global exposurefile
    global familyfile


    donorfile = []
    specimenfile = []
    samplefile = []
    therapyfile= []
    exposurefile = []
    familyfile = []




def readAll (filenames,pcawg):
    #reads in files into the following global variables
    #If one of these files are empty, isPCAWG will always return 0
    global donorfile
    global specimenfile
    global samplefile
    global therapyfile
    global exposurefile
    global familyfile


    for f in filenames:
        #read each file and store it into global lists.
        #in the case where there are multiple files, cut off the header and extend it
        if ".gz" in f:
            lines = gzip.open (f,"r")
        elif ".bz2" in f:
            lines = bz2.BZ2File(f)
        else:
            lines = open (f,"r")
        lines = lines.readlines()

        #if there is already data in these, (i.e multiple files), throw away header
        if "donor" in f:
            if donorfile == []:
                donorfile.extend(lines)
            else:
                donorfile.extend(lines[1:])
        elif "therapy" in f:
            if therapyfile == []:
                therapyfile.extend(lines)
            else:
                therapyfile.extend(lines[1:])
        elif "family" in f:
            if familyfile == []:
                familyfile.extend(lines)
            else:
                familyfile.extend(lines[1:])
        elif "exposure" in f:
            if exposurefile == []:
                exposurefile.extend(lines)
            else:
                exposurefile.extend(lines[1:])
        elif "specimen" in f:
            if specimenfile == []:
                specimenfile.extend(lines)
            else:
                specimenfile.extend(lines[1:])
        elif "sample" in f:
            if samplefile == []:
                samplefile.extend(lines)
            else:
                samplefile.extend(lines[1:])
        else: 
            #this file is not one of donor, specimen or sample
            print "error, what the heck is "+f+"?"

def isPCAWG(someid,filetype):
    #recursively determine if donor is in PCAWG
    #case 1: donor file, need to trace back to any sample 
    #case 2: specimen, trace to any sample
    #case 3: sample check study == 1

    someid = re.split (r'\t',someid) #some sort of id dependant on filetype

    if filetype == "sample":
        if someid[-1].rstrip("\n") == "1": #we assume the last field is the "Study" filed
            return 1
        else:
            return 0
    elif filetype == "specimen":
        specimenid = someid[1]
        #find all lines of this specimenid in sample file
        matching = [s for s in samplefile if specimenid in s]
        for a in matching:
            if isPCAWG(a,"sample") == 1:
                return 1
        return 0
    elif filetype == "donor" or filetype == "family" or filetype == "exposure" or filetype == "therapy":
        donorid = someid[0]
        #find all lines that contain this donorid in specimen file
        matching = [s for s in specimenfile if donorid in s]
        for a in matching:
           if isPCAWG(a,"specimen") == 1:
               return 1
        return 0
    return 0 #if it somehow gets here, just return false


def allowNA (header,index,field):
    pass

def getClinicalPercentage (afile,filehandle,allp,pallp): 
    #obtains %completion for clinical data for given project on given release
    global donorfile
    global specimenfile
    global samplefile
   
    FNULL=open(os.devnull) #pipes command to null

    inputfile = afile #name of file

    #current list we are working on
    
    #determine what kind of file we are reading
    if "donor" in inputfile:
        filetype = "donor"
        currentlist = donorfile
    elif "therapy" in inputfile:
        filetype = "therapy"
        currentlist = therapyfile
    elif "family" in inputfile:
        filetype = "family"
        currentlist = familyfile
    elif "exposure" in inputfile:
        filetype = "exposure"
        currentlist = exposurefile
    elif "specimen" in inputfile:
        filetype = "specimen"
        currentlist = specimenfile
    elif "sample" in inputfile:
        filetype = "sample"
        currentlist = samplefile

    #read in the header
    #what if the project does not have this file?
    if currentlist == []:
        return [0,0,0]
    header= currentlist[0]
    header.rstrip('\n')
    header =  re.split (r'\t', header);

    #declare our bools that check conditions
    #specimen file
    ignore_tumour = False
    ignore_treatment_other = False
    ignore_processing_other = False
    ignore_storage_other= False
    #donor file
    ignore_relationship = False
    ignore_relationship_type = False
    #exposure file
    ignore_smoking_intensity = False
    #therapy
    ignore_therapy1 = False
    ignore_therapy2 = False
    ignore_other_therapy = False

    tumour = [
            "tumour_confirmed",
            "tumour_histological_type",
            "tumour_grading_system",
            "tumour_grade",
            "tumour_grade_supplemental",
            "tumour_stage_system",
            "tumour_stage",
            "tumour_stage_supplemental"
            ]


    relationship = [
            "relationship_type",
            "relationship_type_other",
            "relationship_sex",
            "relationship_age",
            "relationship_disease_icd10",
            "relationship_disease"
            ]

    relationship_other = ["relationship_type_other"]

        
    first_therapy = [
         "first_therapy_response",
         "first_therapy_therapeutic_intent",
         "first_therapy_duration",
         "first_therapy_start_interval"
        ]
    second_therapy = [
         "second_therapy_response",
         "second_therapy_therapeutic_intent",
         "second_therapy_duration",
         "second_therapy_start_interval"
        ]
    
    other_therapy = [
            "other_therapy",
            "other_therapy_response"]


    #depending on file type, check for the indexes of needed fields

    #create a dict that maps each clinical data element to an int
    headcount = [0]*len(header)
    #separate list to count pcawg
    pheadcount = [0]*len(header)

    #read rest of file

    totaldonors = 0 #total for ALL dcc

    pcawgtotal = 0 #total for projects in PCAWG

    for s in currentlist[1:]:
        #go through each line. A line should typically dictate 1 donor/specimen/sample
        s.rstrip('\n')
        totaldonors+=1
        if isPCAWG(s,filetype):
            pcawgtotal+=1
        columns =  re.split (r'\t', s);
        index = 0
        for c in columns:
            if len(header) > index:
                fieldname = header[index]
            else:
                continue
            if c != "" and c != "-777" and c!="-888" and "unknown" not in c:
                if fieldname == "specimen_type" and int(c) in range(101,108):
                    ignore_tumour= True
                elif fieldname == "specimen_donor_treatment_type" and int(c) in range(4,11):
                    ignore_treatment_other=True
                elif fieldname == "specimen_processing" and int(c) in range(1,8):
                    ignore_processing_other=True
                elif fieldname == "specimen_storage" and int(c) in range(1,6):
                    ignore_storage_other == True
                elif fieldname == "donor_has_relative_with_cancer_history":
                    ignore_relationship == True
                elif fieldname == "relationship_type" and int(c) == 7:
                    ignore_relationship == True
                elif fieldname == "relationship_type" and int(c) in range(1,7):
                    ignore_relationship_type == True
                elif fieldname == "tobacco_smoking_history_indicator" and int(c) in range(1,6):
                    ignore_smoking_intensity = True
                elif fieldname == "first_therapy_type" and int(c) == 1:
                    ignore_therapy1 = True
                elif fieldname == "second_therapy_type" and int(c) == 1:
                    ignore_therapy2 = True
                elif fieldname == "first_therapy_type" or fieldname == "second_therapy_type" and int(c) in range (2,11):
                    ignore_other_therapy = True

                headcount[index]+=1
                if isPCAWG(s,filetype):
                    pheadcount[index]+=1
            else:
                #check if we can still count it
                if ((ignore_tumour and fieldname in tumour) or (ignore_treatment_other and fieldname == "specimen_donor_treatment_type_other") or(ignore_processing_other and fieldname == "specimen_processing_other") or(ignore_storage_other and fieldname == "specimen_storage_other") or(ignore_relationship and fieldname in relationship) or(ignore_relationship_type and fieldname == "relationship_type_other") or(ignore_smoking_intensity and fieldname == "tobacco_smoking_intensity") or (ignore_therapy1 and fieldname in first_therapy) or(ignore_therapy2 and fieldname in second_therapy) or(ignore_other_therapy and fieldname in other_therapy)):
                        headcount[index]+=1
                        if isPCAWG(s,filetype):
                            pheadcount[index]+=1
                 
                if fieldname == "relationship_type":
                    ignore_relationship_type = True
                elif fieldname == "other_therapy":
                    ignore_other_therapy = True
                 
            index+=1 
    count = 0

    avgtotal =0;
    pcavgtotal=0;

    #write to all tables and logfile
    if filetype == "donor":
        filehandle.write ("field_name\tdcc_completion\tPCAWG_completion\n")
    for field in header:
        field =field.rstrip("\n")
        field =field.rstrip("\t")
    
        filehandle.write (field+"\t"+"{:.1%}".format(headcount[count]/totaldonors)+"\t")
        allp.write ("{:.1%}".format(headcount[count]/totaldonors)+"\t")
        avgtotal += headcount[count]/totaldonors
        if pcawgtotal != 0:
            filehandle.write ("{:.1%}".format(pheadcount[count]/pcawgtotal)+"\n")
            pallp.write ("{:.1%}".format(pheadcount[count]/pcawgtotal)+"\t")
            pcavgtotal += pheadcount[count]/pcawgtotal
        else:
            filehandle.write ("N/A\n")
            pallp.write ("N/A\t")
        count+=1

    return [avgtotal,pcavgtotal,len(headcount)]


def getWGS (release,projkey,output,alldiat): #STR STR FILEHANDLE FILEHANDLE

    #these are the sequencing strategies in wholegenome files that contribute o the count

    addtocount = 'WGS','WXS','WGA'

    #initiate empty dictonary that maps a sequencing strategy to a list of donors

    data = dict()

    #declare FNULL to pipe curl outputs

    FNULL=open(os.devnull)

    #output.write("\n"+release+"EQUALSEQUALS\t")

    #WHOLE GENOMES
    filelist = []
    wholegenome = ["simple_somatic_mutation.open","structural_somatic_mutation", "copy_number_somatic_mutation", "splice_variant", "simple_somatic_mutation"]

    #larger RNA-SEQ and METH-ARRAY files. They are not included by default since these files are exceptionally large
    rnaseq = ["mirna_seq","exp_seq"]

    epigen = ["meth_seq"]

    protein = ["protein_expression"]

    arraybase = ["meth_array","exp_array"] #these don't have sequencing strategies, need to do a cross-check with final whole genome count

    filelist.extend(wholegenome)
    filelist.extend(rnaseq)
    filelist.extend(epigen)
    filelist.extend(protein)
    filelist.extend(arraybase)


    #attempt to download each file
    for filename in filelist:
        print ".",

        if release == '12': #release 12 has different file structure
            #command = "curl --fail -o "+filename+".gz https://dcc.icgc.org/api/v1/download?fn=/legacy_data_releases/release_"+str(release)+"/"+projkey+"/"+filename+"."+projkey+".tsv.gz"
            pass
        elif release == '14': #14 and 15 don't have project page
            command = "curl --fail -o "+filename+".gz https://dcc.icgc.org/api/v1/download?fn=/release_"+str(release)+"/"+projkey+"/"+filename+"."+projkey+".tsv.gz"
            check = "curl --fail --silent --head -o /dev/null https://dcc.icgc.org/api/v1/download?fn=/release_"+str(release)+"/"+projkey+"/"+filename+"."+projkey+".tsv.gz"
        elif release == '15': #15 needs to be 15.1 
            command = "curl --fail -o "+filename+".gz https://dcc.icgc.org/api/v1/download?fn=/release_"+str(release)+".1/"+projkey+"/"+filename+"."+projkey+".tsv.gz"
            check = "curl --fail --silent --head -o /dev/null https://dcc.icgc.org/api/v1/download?fn=/release_"+str(release)+".1/"+projkey+"/"+filename+"."+projkey+".tsv.gz"
        else: #16 to 18 and hopefully beyond
            command = "curl --fail -o "+filename+" https://dcc.icgc.org/api/v1/download?fn=/release_"+str(release)+"/Projects/"+projkey+"/"+filename+"."+projkey+".tsv.gz"
            check = "curl --fail --silent --head -o /dev/null https://dcc.icgc.org/api/v1/download?fn=/release_"+str(release)+"/Projects/"+projkey+"/"+filename+"."+projkey+".tsv.gz"
        

        #continue only if there's actually an url at specified 'check' url
        if  checkExistURL(check) != 0:
            continue

        #executes the download

        process  = subprocess.Popen(command.split(),stdout=FNULL,stderr=subprocess.STDOUT)
        process.communicate

        process.wait()

        if process.returncode != 0: #should always be 0, but just in case
            print "Attempted to download URL that doesn't exist"
            continue

        #unzip the files, not needed. We use gzip read instead
        #gunzipFiles(filename)
    

    #as we go through each file, also put donors in these categories
    alldna = []
    allrnaseq = []
    allepigenome = []
    allprotein = []
    allarray = []

    for a in filelist: 

        #goes through each downloaded file and gets needed data

        try:
            input = gzip.open (a,'r') #open input gzip file
        except:
            #don't have this file, skip to next iteration
            continue

        #parse the header, check which index for desired header

        s = input.readline()
        header =  re.split (r'\t', s);
        
        if 'sequencing_strategy' in header:
            sindex = header.index('sequencing_strategy')
        else:
            sindex = -1

        dindex = header.index('icgc_donor_id')

#        print "Sequencing Strategy Index:", sindex
#        print "Donor ID index:", dindex

        for d in input:
            line =  re.split (r'\t', d)
            if sindex != -1:
                tempstrat = line[sindex]
            else: 
                tempstrat = a
            tempdonor = line[dindex]

            #at this point, we have a pair [strategy:donor]

            #add this donor to the appropriate category
            if tempstrat != "Non-NGS":
                if a in wholegenome:
                    #this is our 100%
                    if tempdonor not in alldna and tempstrat in addtocount:
                        alldna.append(tempdonor)
                elif a in rnaseq:
                    if tempdonor not in allrnaseq:
                        allrnaseq.append(tempdonor)
                elif a in epigen:
                    if tempdonor not in allepigenome:
                        allepigenome.append(tempdonor)
                elif a in protein:
                    if tempdonor not in allprotein:
                        allprotein.append(tempdonor)
                elif a in arraybase:
                    if tempdonor not in allarray:
                        allarray.append(tempdonor)

            if tempstrat in data:
                #key exists. Check if the donor is unique
                if tempdonor not in data[tempstrat]:
                    data[tempstrat].append(tempdonor)
            else:
                data[tempstrat] = [tempdonor]

        input.close()

        # print out # of unique donors for each sequencing strategy found in file
    total = []; #to be a list of unique donors within desired sequencing strategy

    output.write(release+"\t")

    print "Project Key: "+projkey+" Release:"+release

    for strategy in data:
        print len(data[strategy]), "unique donors for", strategy
        if strategy in addtocount:
            total = addUniq(total,data[strategy])
    #print each strategy
    for strat in addtocount:
        if strat in data:
            output.write (str(len(data[strat]))+"\t") 
        else:
            output.write ("x\t") 

    deleteFiles(filelist)

    print "Metrics:"
    print "DNA:"+str(len(alldna))
    print "RNASEQ:"+str(len(common_elements(allrnaseq,alldna)))
    print "EPIGENOME:"+str(len(common_elements(allepigenome,alldna)))
    print "PROTEIN:"+str(len(common_elements(allprotein,alldna)))
    print "ARRAY-BASED:"+str(len(common_elements(allarray,alldna)))


    finalnum =0 
    #add it into the total count
    if len(total)!= 0:
        print "Final count (unique donors within WGS,WXS,WGA): "+str(len(total))
        finalnum = len(total)
    elif len(total) == 0 and not data:
        #No files were found in the release, will return -1
        finalnum = -1
    else:
        #found stuff in release, but total is 0
        print "Data was in this release, but no donors for desired sequencing strategies"
        finalnum = 0

    #write to log file
    output.write (str(finalnum)+"\n") 
    #write to big table
    alldat.write (str(finalnum)+"\t") 


    return finalnum

#doge = open ("t","w")
#getWGS(sys.argv[1],sys.argv[2],doge,doge)
#readAll(sys.argv[1:])
#for a in sys.argv[1:]:
#    getClinicalPercentage (a) #STR STR FILEHANDLE
