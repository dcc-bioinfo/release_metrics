import os
import re
import json
import sys
import pprint


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
    #hardcoded dict info
    #dict mapping then name of the error to ["DESC","CODE"]
    errors = {
            "donor_survival_time":["Donor survival time must be submitted if donor is deceased. If donor is alive and in complete remission, relapse or progression, donor survival time should be equal to the donor interval of last followup. If the donor is deceased and was in complete remission, relpase or progression, the donor survival time should be less than or equal to the donor relpase interval but greater than or equal to the donor interval of last followup.","""
                complete_remission = (disease_status_last_followup == '1'); 
                progression = (disease_status_last_followup == '3'); 
                relapse = (disease_status_last_followup == '4'); 
                alive = (donor_vital_status == '1'); 
                deceased = (donor_vital_status == '2'); 

                if (deceased && donor_survival_time == null){ return false } 
                else if ( (donor_survival_time != null && donor_interval_of_last_followup !=  null) && (complete_remission || progression || relapse) ) { 
                   if (alive) { 
                             donor_survival_time == donor_interval_of_last_followup 
                                } else if (deceased) { 
                                          donor_survival_time <= donor_interval_of_last_followup 
                                             } else { return true }
                                } else { return true }
                """],
            "donor_relapse_interval":["If donor is alive and in complete remission, relapse or progression, the donor relapse interval should be less than or equal to the donor interval of last followup. If the donor is decesased and was in complete remission, relapse or progression, the donor relapse interval should be less than or equal to the donor survival time.","""
                complete_remission  = (disease_status_last_followup ==  '1'); donor_primary_treatment_interval
                progression = (disease_status_last_followup ==  '3'); 
                relapse = (disease_status_last_followup ==  '4'); 
                alive = (donor_vital_status ==  '1'); 
                deceased  = (donor_vital_status ==  '2'); 

                if  (donor_relapse_interval !=  null){  
                        if  (progression  ||  relapse){ 
                                    if  (alive){  
                                                    if  (donor_interval_of_last_followup  !=  null){  
                                                                        return  donor_relapse_interval  <=  donor_interval_of_last_followup 
                                                                                    } 
                                                            }else if  (deceased){ 
                                                                            if  (donor_survival_time  !=  null){  
                                                                                                return  donor_relapse_interval  <=  donor_survival_time 
                                                                                                            } 
                                                                                    } 
                                                                } 
                        } 
                return  true  
                """],
            "donor_age_at_enrollment":["The donor's age at enrollment must be expressed in years. If donor is older than 90 years old, submit value of 90. The donor age at enrollment should be greater than or equal to the donor's age at last followup","""
                if (donor_age_at_enrollment > 90) { 
                    return false }
                if (donor_age_at_enrollment > donor_age_at_last_followup) {
                    return false}
                return true
                """],
            "donor_age_at_diagnosis":["The donor's age at diagnosis must be expressed in years. If donor is older than 90 years, submit value of 90. The donor's age at diagnosis should be less than or equal to the donor's age at enrollment","""
                if (donor_age_at_diagnosis > 90) { 
                    return false }
                if (donor_age_at_diagnosis > donor_age_at_last_followup) {
                    return false}
                return true
                                """],
                "donor_age_at_last_followup":["The donor's age at last followup must be expressed in years. If the donor is older than 90 years old, submit value of 90.","""
                if (donor_age_at_last_followup > 90) { return false } return true
                                             """]
            }

    inputfile = sys.argv[1]

    #open output file
    projectfile = inputfile.split("_")

   # outfile = open (projectfile[0]+".error",'w')


    print "PROJECT: ", projectfile[0], "\n"

    filedata = open (inputfile).read()
    jsondata = json.loads(filedata)

    #print project data

    genError(jsondata,errors)

    #print name
    #print issue

    #test print
    #print (jsondata['dataTypeReports'][0]['fileTypeReports'][2]['fileReports'][0]['errorReports'])

main()
