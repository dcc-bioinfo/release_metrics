from __future__ import division
import os
import re
import sys

def main():
    pcawgfields = open ("uniqpcawg.txt",'r')
    pcawgfields = pcawgfields.readlines()
    pcawgfields = map (lambda s: s.strip(), pcawgfields)

    directory = sys.argv[1]
    print "Project_name\t",
    print ('\t'.join(map(str,pcawgfields))),
    print "average" 
    
    for filename in os.listdir(directory):
        if "clinical_percentages" in filename:
            totaldcc =0
            totalpcawg=0

            summary = open (directory+"/"+filename,'r')

            summarylist = summary.readlines()

            print filename,

            for field in pcawgfields:
                matches = [s for s in summarylist if field in s]  
                if matches != []:
                    printed = False
                    for match in matches:
                        split = re.split(r'\t',match)
                        if field != split[0]:
                            #checks for exact match
                            continue
                        elif printed == False:
                            if "N/A" not in split[1]:
                                totaldcc += float(split[1][:-1])
                            if "N/A" not in split[2]: 
                                totalpcawg += float(split[2][:-2])
                            print (split[2][:-2]),
                            printed = True
                else:
                    print "0.0",

            average = str(float(totaldcc)/len(pcawgfields))
            paverage = str(float(totalpcawg)/len(pcawgfields))

            print paverage

main()
