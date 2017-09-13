import argparse
import logging
import os
import sys
from string import Template

SCHEMA_FLAT = ["Category", "Place", "Bib", "Name", "Team name", "Age", "Year of birth", "Time"]
SCHEMA_RESHAPE = ["Lap", "Lap time"]
DEFAULT_CATEGORY = "Cat 1/2 Men"
DEFAULT_VALUE = "-"

IN_DELIM = "\t"
OUT_DELIM = ","

def main(inFoldName, outFileName):
    logger = logging.getLogger(__name__)
    
    file_list = getFiles(inFoldName)
    with open(outFileName, "w") as outF:
        writeHeader(outF)
        for file in file_list:
            processFile(file, outF)
        logger.info("All data written to " + outFileName)
        

def getFiles(inFoldName):
    logger = logging.getLogger(__name__)
    logger.info("Searching for files in " + inFoldName)
    logger.debug("Contents:")
    
    files = []
    for test in os.listdir(inFoldName):
        test = os.path.join(inFoldName, test)
        if not os.path.isfile(test):
            logger.debug(" " + test + " - Not a file")
            continue
        if test[-4:] != ".txt":
            logger.debug(" " + test + " - Skipped (looking for .txt files)")
            continue
        logger.debug(" " + test)
        files.append( test )
    return files

def writeHeader(outF):
    outF.write(OUT_DELIM.join(SCHEMA_FLAT))
    outF.write(OUT_DELIM)
    outF.write(OUT_DELIM.join(SCHEMA_RESHAPE))
    outF.write("\n")

def isHeader(line):
    return "Place" in line and "Bib" in line

def isBlank(line):
    return not line.strip()
def getNumLaps(line):
    return len(line.split(IN_DELIM)) - IGNORED_COLS - (S_FLAT_E-S_FLAT_S)

def isDNS(line):
    return line.startswith("-")

def isCategory(line):
    return line.startswith("\t\t")
def getCategory(line):
    return line.strip()

def getFlatRow(schema_map):
    row = []
    for col in SCHEMA_FLAT:
        row.append(schema_map[col])
    return OUT_DELIM.join(row)

def writeReshapedData(outF, flatRow, schema_map):
    lap = 1
    col = Template("Lap $lap").substitute(lap=lap)
    while col in schema_map:
        outF.write(flatRow)
        outF.write(OUT_DELIM)
        outF.write(OUT_DELIM.join([str(lap), schema_map[col]]))
        outF.write("\n")
        
        lap += 1
        col = Template("Lap $lap").substitute(lap=lap)

def processFile(file, outF):
    logger = logging.getLogger(__name__)
    logger.info("Processing " + file)
    
    default_values ={}
    for col in SCHEMA_FLAT:
        default_values[col] = DEFAULT_VALUE
    default_values["Category"] = DEFAULT_CATEGORY
    schema = SCHEMA_FLAT

    num_laps = -1
    with open(file, "r") as inF:
        for line in inF:
            if isHeader(line):
                schema = line.split(IN_DELIM)
                continue
            if isBlank(line):
                continue
            if isDNS(line):
                continue
            if isCategory(line):
                default_values["Category"] = getCategory(line)
                continue

            # else it's a racer with a place
            vars = line.split(IN_DELIM)
            schema_map = default_values.copy()
            for i in range(len(schema)):
                if "Place" in schema[i]: # Weird case where this gets extra noise in the Cat 1/2 Men single file
                    schema[i] = "Place"
                vars[i] = vars[i].replace("\"","").replace("\'","").replace(",","")
                schema_map[schema[i].strip()] = vars[i]
            flat_row = getFlatRow(schema_map)
            writeReshapedData(outF, flat_row, schema_map)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    
    parser = argparse.ArgumentParser(description="Process MFG race results into a single Tableau-readable\
    file")
    parser.add_argument('inFoldName', metavar='inputFolder', help='Path to the folder containing the result\
    files for each start time, download from webscorer using "Download complete results"/"Tab-delimited\
    TXT file"')
    parser.add_argument('outFileName', metavar='outputFile', help="Path/name of the csv file to be created\
    for feeding into Tableau")
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument("-v", action="store_true", help="Print verbose information about program process")
    args = parser.parse_args()
    
    if args.v:
        logger.setLevel(logging.DEBUG)
    main(args.inFoldName, args.outFileName)