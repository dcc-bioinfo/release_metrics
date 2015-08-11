import os
import re
import json
import sys
import pprint
import gzip


def genError (data,errors):
    # go through to needed level
    for i in range(len(data['dataTypeReports'])):

        for filepos in range(len((data['dataTypeReports'][i]['fileTypeReports']))):

            for fileReportPos in range(len(data['dataTypeReports'][i]['fileTypeReports'][filepos]['fileReports'])):

             #for reach FILE (clinical, etc) get the error(s)
             errorReport = data['dataTypeReports'][i]['fileTypeReports'][filepos]['fileReports'][fileReportPos]['errorReports']

             #print "ERROR REPORT = %s\n"%errorReport
             if (len(errorReport) != 0):

                    #if the error is not empty, go through each one
                    for report in range(len(errorReport)):
                        print "Error type = %s"%(errorReport[report]['errorType']),"\n"

                        for fieldErrors in range(len(errorReport[report]['fieldErrorReports'])):
                            print "ERROR: ", fieldErrors+1
                            errorType =(errorReport[report]['fieldErrorReports'][fieldErrors]['fieldNames'][0])
                            print "COLUMN: ", errorType

                            print "DESCRIPTION: ",
                            print errors[errorType][0]

                            print "SCRIPT: "
                            print errors[errorType][1]

                            print "COUNT: "
                            print (errorReport[report]['fieldErrorReports'][fieldErrors]['count'])
                            print "LINENUMBERS: "
                            print (errorReport[report]['fieldErrorReports'][fieldErrors]['lineNumbers'])
                            print "VALUES: "
                            for errorline in errorReport[report]['fieldErrorReports'][fieldErrors]['values']:
                                print errorline
                            #print (errorReport[report]['fieldErrorReports'][fieldErrors]['values'])

                            print ""
    
def main():
    #get all the files from the folder

    #hardcoded dict info
    #dict mapping then name of the error to ["DESC","CODE"]
    errors = {
            "donor_survival_time":["""
When donor is deceased:

        -donor_survival_time is required. 
        -When "donor_interval_of_last_followup" has a value, it must be greater than or equal to "donor_survival time".

When donor is alive:

        -If "donor_survival_time" and "donor_interval_of_last_followup" have values, "donor_survival_time" must equal "donor_interval_of_last_followup"
""","""
alive = (donor_vital_status == '1'); 
deceased = (donor_vital_status == '2'); 
 
if (deceased) { 
   if (donor_survival_time == null) { 
      return false 
   } 
   if (donor_interval_of_last_followup != null) { 
      if (!(donor_survival_time <= donor_interval_of_last_followup)) { 
         return false 
      } 
   } 
} 
 
if (alive) { 
   if (donor_survival_time != null && donor_interval_of_last_followup != null) { 
      if (!(donor_survival_time == donor_interval_of_last_followup)) { 
         return false 
      }
   } 
} return true
                       """],
            "donor_relapse_interval":["""
If the donor's disease status at last followup was progression or relapse:

        -"donor_relapse_interval" is required.

If the donor is alive:

            -"donor_relapse_interval" should be less than or equal to "donor_interval_of_last_followup"

If donor is deceased:

            -"donor_relapse_interval" should be less then or equal to "donor_survival_time".
""","""
alive = (donor_vital_status == '1'); 
deceased = (donor_vital_status == '2'); 
progression = (disease_status_last_followup == '3'); 
relapse = (disease_status_last_followup == '4'); 
 
 
if (progression || relapse ) { 
   if (donor_relapse_interval == null || donor_interval_of_last_followup == null) { 
      return false 
   } 
 
   if (alive && !(donor_relapse_interval <= donor_interval_of_last_followup)) { 
      return false 
   } 
 
   if (deceased && !(donor_relapse_interval <= donor_survival_time)) { 
      return false 
   } 
} return true
                     """],
            "donor_age_at_enrollment":["""
    -If the donor is older than 90 years, default value of 90 should be used. 
    -The donor's age at enrollment should be less than or equal to the donor's age at last_followup
""","""
if (donor_age_at_enrollment > 90) { 
    return false }
if (donor_age_at_enrollment > donor_age_at_last_followup) {
    return false}
return true
"""],
            "donor_age_at_diagnosis":["""
    -If the donor is older than 90 years, default value of 90 should be used. 
    -The donor's age at diagnosis should be less than or equal to the donor's age at enrollment
""","""
if (donor_age_at_diagnosis > 90) { 
    return false }
if (donor_age_at_diagnosis > donor_age_at_last_followup) {
    return false}
return true
                """],
                "donor_age_at_last_followup":["The donor's age at last followup must be expressed in years. If the donor is older than 90 years old, submit value of 90.","""
if (donor_age_at_last_followup > 90) { return false } return true
                                             """],
            "donor_interval_of_last_followup":["""
If the disease status at last followup was progression or relapse:
    - "donor_interval_of_last_followup" field is required
            """,
            """
progression = (disease_status_last_followup == '3'); 
relapse = (disease_status_last_followup == '4'); 
 
if (progression || relapse) { 
   if (donor_interval_of_last_followup == null) { 
      return false 
   } 
} return true
            """]
            }

    inputfile = sys.argv[1]

    #open output file
    projectfile = inputfile.split("_")

    # outfile = open (projectfile[0]+".error",'w')

    print "PROJECT: ", projectfile[0], "\n"
    if ".gz" in inputfile:
        filedata = gzip.open (inputfile).read()
    else:
        filedata = open (inputfile).read()

    jsondata = json.loads(filedata)

    #print project data

    genError(jsondata,errors)

    #print (jsondata['dataTypeReports'][0]['fileTypeReports'][2]['fileReports'][0]['errorReports'])

main()
