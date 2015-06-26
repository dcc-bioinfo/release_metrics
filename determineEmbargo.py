#takes project key, determines which release it was submitted to and # of WGS for every release past that
import sys
import os
import re
import subprocess
import parseForWGS
from datetime import *
import time
from optparse import OptionParser


#gathers embargo data for 1 project key

if len(sys.argv) == 1:
    print "Enter project key as parameter"
    sys.exit()

projkey = sys.argv[1]

print "========================="+projkey+"============================"

output = open (projkey+".data",'w') #file that stores some data for each project 

output.write ("release\tWGS\tWXS\tWGA\ttotal_donor\n") #header

#file that stores data for every project
#header is PROJKEY RELEASES EMBARGO STATUS

alldat = open ("all.data",'a') #opens in append mode

#write the project code

alldat.write (projkey+"\t")

#list of projects that existed in v.12. 

inr12 = "ALL-US","BLCA-US","BRCA-US","CESC-US","CLLE-ES","COAD-US","GACA-CN","GBM-US","HNSC-US","KIRC-US","KIRP-US","LICA-FR","LINC-JP","LIRI-JP","LIHC-US","LGG-US","LUAD-US","LUSC-US","MALY-DE","OV-US","PACA-US","PACA-CA","PACA-AU","PBCA-DE","PEME-CA","PRAD-US","PRCA-CA","PRCA-UK","READ-US","SKCM-US","UCEC-US","LAML-US","BRCA-UK","CMDI-UK","EOPC-DE","PRAD-UK","PRAD-CA","STAD-US","THCA-US"

#quickly check if projkey is in 12 so we can write to all table
if projkey in inr12:
    alldat.write ("y\t")
else:
    alldat.write ("n\t")

#object for 1 year and 2 year periods

oneyear = timedelta(days=365)
twoyear = timedelta(days=365*2)

#dict mapping release # int to date objects
releasedates = {
        12 :  date(2013, 3, 27),
        13 :  date(2013, 9, 26), #same as 14
        14 :  date(2013, 9, 26),
        15 :  date(2014, 2, 12), #use 15.1 date
        16 :  date(2014, 5, 15),
        17 :  date(2014, 9, 12),
        18 :  date(2015, 1, 15),
        19 :  date(2015, 6, 16)
        }


#do release 13-current. For now, ignore release 12

#download command

FNULL = open(os.devnull)

initial = 0
first100 = 0


#since release 13 and 14 are on the same date, release 13 doesn't really matter. If it was introduced in release 13, we can assume it was released in 14. Then, we check release 12 to see if 2 years have already passed.

for release in range (14,20): #release 13 and below uses legacy format

    total = parseForWGS.getWGS(str(release),projkey,output,alldat) #STR STR FILEHANDLE

    if total == -1:
        print "not in release", str(release)
    else:
        print "found in release", str(release)

        if initial == 0:
            if release == 14:
                print "WARN: Data not recorded for legacy releases"
            if projkey in inr12:
                initial = 12
            else:
                initial = release
        
        #find when it got 100 genomes
        if int(total) >= 100 and first100 == 0:
            first100 = release


if initial == 0:
    print "Project was not found in release 14-19."
    #remove data
    os.remove(projkey+".data")
    alldat.write("\n")
    sys.exit()

print "First release was "+str(initial)+" on date:",
print releasedates[initial]
print "Date that reached 100 WGS:",
if first100 != 0:
    print releasedates[first100]
else:
    print "never"

#embargo status

output.write (projkey + " embargo status: ")


def determineEmbargo (initial, first100): #DATEOBJECT DATEOBJECT
    #case 1 full 2 years. Release 12 or lower initial
    #case 2, first100 == initial. Add 1 year
    #case 3, first100 > initial, but time between those releases is less than 1 yr. Then add 1yr to first100
    #case 4, first100 > inital, but over 1 yr apart. Wait full 2 yr.

    today = date.today()

    if (initial <= 12): #since the project existed at release 12, we can assume that it has been 2 years.
        print "Release is more than 2 years old"
        print "No Embargo"
        output.write ("No Embargo")
        alldat.write ("No Embargo")
    elif (first100 == 0):  #never got 100, calculate 2 years
        print "Does not have 100 wgs"
        if ((releasedates[initial] + twoyear) > today):
            print "Will be lifted on",
            print releasedates[initial]+twoyear
            output.write ((releasedates[initial]+twoyear).isoformat())
            alldat.write ((releasedates[initial]+twoyear).isoformat())
        else:
            print "No Embargo"
            output.write ("No Embargo")
            alldat.write ("No Embargo")
    elif (initial == first100): #case 2, had 100 form beginning
        print "Had 100 wgs at release"
        if ((releasedates[initial] + oneyear) > today):
            print "Will be lifted on",
            print releasedates[initial]+oneyear
            output.write ((releasedates[initial]+oneyear).isoformat())
            alldat.write ((releasedates[initial]+oneyear).isoformat())
        else:
            print "No Embargo"
            output.write ("No Embargo")
            alldat.write ("No Embargo")
    elif (initial < first100): #case 3 and 4
        timeperiod = releasedates[first100] - releasedates[initial]
        if timeperiod.days > 365:
            print "100 wgs reached after 1 year"
            #2 years from initial
            if ((releasedates[initial] + twoyear) > today):
               print "Will be lifted on",
               print releasedates[initial]+twoyear
               output.write ((releasedates[initial]+twoyear).isoformat())
               alldat.write ((releasedates[initial]+twoyear).isoformat())
            else:
                print "No Embargo"
                output.write ("No Embargo")
                alldat.write ("No Embargo")
        else:
            #1 year from first100
            print "100 wgs reached within 1 year"
            if ((releasedates[first100] + oneyear) > today):
               print "Will be lifted on",
               print releasedates[first100]+oneyear
               output.write ((releasedates[first100]+oneyear).isoformat())
               alldat.write ((releasedates[first100]+oneyear).isoformat())
            else:
                print "No Embargo"
                output.write ("No Embargo")
                alldat.write ("No Embargo")

 
    output.write ("\nInitial Release: "+str(initial)+"(or before if 12),reached 100 whole genomes on release "+str(first100)+"(0 means it never reached 100)")
    alldat.write ("\n")

determineEmbargo(initial, first100) #INT INT


output.close() 

#we might as well delete the file is there is no data
