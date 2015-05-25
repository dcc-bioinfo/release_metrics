Set of scripts to parse and collect ICGC project data.

determineEmbargo.py: Calculates embaro status for 1 project. Input is ONE project key.

findClinical.py: Calculates clinical completeness for all projects. Input is the root folder containing all the project's raw data.

generateall.sh: Simple bash script to call determineEmbargo across all projects.

makemapping.py: Used on the output table of determineEmbargo to add project information to the table.

parseForWGS: Poorly named script that contains multiple functions that are called by determineEmbargo and findClinical.
