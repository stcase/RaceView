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

class Reshaper:
    """ Reshapes race results with lap data into a Tableau-readable form """

    def __init__(self, inFoldName, outFileName):
        self.__logger = logging.getLogger(__name__)  
        self.__inFoldName = inFoldName
        self.__outFileName = outFileName
        
        self.__rawFiles = []

    def getFiles(self):
        self.__logger.info("Searching for files in " + self.__inFoldName)
        self.__logger.debug("Contents:")
        
        files = []
        for test in os.listdir(self.__inFoldName):
            test = os.path.join(self.__inFoldName, test)
            if not os.path.isfile(test):
                self.__logger.debug(" " + test + " - Not a file")
                continue
            if test[-4:] != ".txt":
                self.__logger.debug(" " + test + " - Skipped (looking for .txt files)")
                continue
            self.__logger.debug(" " + test)
            files.append( test )
        self.__rawFiles = files
        
    def outputData(self):
        with open(self.__outFileName, "w") as outF:
            self.__writeHeader(outF)
            self.__logger.debug("Processing:")
            for file in self.__rawFiles:
                self.__logger.debug(" " + file)
                self.__processFile(file, outF)
            self.__logger.info("All data written to " + self.__outFileName)

    def __writeHeader(self, outF):
        outF.write(OUT_DELIM.join(SCHEMA_FLAT))
        outF.write(OUT_DELIM)
        outF.write(OUT_DELIM.join(SCHEMA_RESHAPE))
        outF.write("\n")

    def __isHeader(self, line):
        return "Place" in line and "Bib" in line

    def __isBlank(self, line):
        return not line.strip()
        
    def __getNumLaps(self, line):
        return len(line.split(IN_DELIM)) - IGNORED_COLS - (S_FLAT_E-S_FLAT_S)

    def __isDNS(self, line):
        return line.startswith("-")

    def __isCategory(self, line):
        return line.startswith("\t\t")

    def __getCategory(self, line):
        return line.strip()

    def __getFlatRow(self, schema_map):
        row = []
        for col in SCHEMA_FLAT:
            row.append(schema_map[col])
        return OUT_DELIM.join(row)

    def __writeReshapedData(self, outF, flatRow, schema_map):
        lap = 1
        col = Template("Lap $lap").substitute(lap=lap)
        while col in schema_map:
            outF.write(flatRow)
            outF.write(OUT_DELIM)
            outF.write(OUT_DELIM.join([str(lap), schema_map[col]]))
            outF.write("\n")
        
            lap += 1
            col = Template("Lap $lap").substitute(lap=lap)

    def __processFile(self, file, outF):
        default_values ={}
        for col in SCHEMA_FLAT:
            default_values[col] = DEFAULT_VALUE
        default_values["Category"] = DEFAULT_CATEGORY
        schema = SCHEMA_FLAT

        num_laps = -1
        with open(file, "r") as inF:
            for line in inF:
                if self.__isHeader(line):
                    schema = line.split(IN_DELIM)
                    continue
                if self.__isBlank(line):
                    continue
                if self.__isDNS(line):
                    continue
                if self.__isCategory(line):
                    default_values["Category"] = self.__getCategory(line)
                    continue

                # else it's a racer with a place
                vars = line.split(IN_DELIM)
                schema_map = default_values.copy()
                for i in range(len(schema)):
                    if "Place" in schema[i]: # Weird case where this gets extra noise in the Cat 1/2 Men single file
                        schema[i] = "Place"
                    vars[i] = vars[i].replace("\"","").replace("\'","").replace(",","")
                    schema_map[schema[i].strip()] = vars[i]
                flat_row = self.__getFlatRow(schema_map)
                self.__writeReshapedData(outF, flat_row, schema_map)


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

    reshaper = Reshaper(args.inFoldName, args.outFileName)
    reshaper.getFiles()
    reshaper.outputData()
