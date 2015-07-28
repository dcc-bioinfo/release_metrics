import os,sys,re
from subprocess import call
import bz2
import gzip

call ("ssh-keygen -R hproxy-dcc.res.oicr.on.ca",shell=True)

def scpdonors (projectcode):

    call ( "sshpass -p 'Meowmoko12' scp kchen@hproxy-dcc.res.oicr.on.ca:/hdfs/dcc/icgc/submission/ICGC20/"+projectcode+"/donor* TEST" ,shell=True)


def main ():
    #open the big pcawg table

    pcawgfilelines = open(sys.argv[1],'r').readlines()

    pcawglist = open(sys.argv[2],'r').readlines()

    usfilemap = open(sys.argv[3],'r').readlines()

    
    for pcawgproj in pcawglist:
        pcawgproj = pcawgproj.rstrip('\n')
        scpdonors (pcawgproj)


        #open the donorfile for target project
        donorfilelines = []
        for donorfile in os.listdir("TEST"):

            if "bz2" in donorfile:
                donorfilelines.extend(bz2.BZ2File("TEST/"+donorfile).readlines())
            elif "gz" in donorfile:
                donorfilelines.extend(gzip.open("TEST/"+donorfile).readlines())
            else:
                donorfilelines.extend(open("TEST/"+donorfile,'r').readlines())
            
            os.remove("TEST/"+donorfile)
            #get the project key


        matching = [s for s in pcawgfilelines if pcawgproj in s]

        for line in matching:
            donoridcode = line.split('\t')[0]
            donorid = line.split('\t')[1]

            if "-US" in pcawgproj:
                #find the special us CODE
                donorid = [s for s in usfilemap if donorid in s.split('\t')[1]]
                 
                if donorid != []:
                    donorid = donorid[0].split('\t')[2]
                else:
                    print ("could not map")

            donorid = donorid.rstrip('\n')
            donormatch = [s for s in donorfilelines if donorid in s.split('\t')[0]]

            if donormatch == []:
                if "-US" in pcawgproj:
                    print (pcawgproj+"::"+donorid)
                else:
                    print (donoridcode)

main()
