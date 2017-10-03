import argparse
import logging
import os
import sys
from string import Template


class Reshaper:
    """ Reshapes race results with lap data into a Tableau-readable form """

    def __init__(self, inFoldName, outFileName, raceName=""):
        self.__logger = logging.getLogger(__name__)  
        self.__inFoldName = inFoldName
        self.__outFileName = outFileName
        
        self.__rawFiles = []
        
        self.__NUM_EXPECTED_FILES = 7
        self.__SCHEMA_FLAT = ["Category", "Place", "Bib", "Name", "Team name", "Age", "Year of birth", "Time"]
        self.__SCHEMA_RESHAPE = ["Lap", "Lap time"]
        self.__DEFAULT_VALUE = "-"
        self.__IN_DELIM = "\t"
        self.__OUT_DELIM = ","
        self.__DEFAULT_VALUES = {}
        for col in self.__SCHEMA_FLAT:
            self.__DEFAULT_VALUES[col] = self.__DEFAULT_VALUE
        self.__DEFAULT_VALUES["Category"] = "Cat 1/2 Men"
        if  raceName:
            self.__DEFAULT_VALUES["Race"] = raceName
            self.__SCHEMA_FLAT.insert(0, "Race")

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
            
        if len(files) != self.__NUM_EXPECTED_FILES:
            self.__logger.warn("Expected " + str(self.__NUM_EXPECTED_FILES) + " race files, only " + str(len(files)) + " present.")
            
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
        outF.write(self.__OUT_DELIM.join(self.__SCHEMA_FLAT))
        outF.write(self.__OUT_DELIM)
        outF.write(self.__OUT_DELIM.join(self.__SCHEMA_RESHAPE))
        outF.write("\n")

    def __isHeader(self, line):
        return "Place" in line and "Bib" in line

    def __isBlank(self, line):
        return not line.strip()
        
    def __getNumLaps(self, line):
        return len(line.split(self.__IN_DELIM)) - IGNORED_COLS - (S_FLAT_E-S_FLAT_S)

    def __isDNS(self, line):
        return line.startswith("-")

    def __isCategory(self, line):
        return line.startswith("\t\t")

    def __getCategory(self, line):
        return line.strip()

    def __getFlatRow(self, schema_map):
        row = []
        for col in self.__SCHEMA_FLAT:
            row.append(schema_map[col])
        return self.__OUT_DELIM.join(row)

    def __writeReshapedData(self, outF, flatRow, schema_map):
        lap = 1
        col = Template("Lap $lap").substitute(lap=lap)
        while col in schema_map:
            outF.write(flatRow)
            outF.write(self.__OUT_DELIM)
            outF.write(self.__OUT_DELIM.join([str(lap), schema_map[col]]))
            outF.write("\n")
        
            lap += 1
            col = Template("Lap $lap").substitute(lap=lap)

    def __processFile(self, file, outF):
        default_values = self.__DEFAULT_VALUES.copy()
        schema = self.__SCHEMA_FLAT

        num_laps = -1
        with open(file, "r") as inF:
            for line in inF:
                if self.__isHeader(line):
                    schema = line.split(self.__IN_DELIM)
                    continue
                if self.__isBlank(line):
                    continue
                if self.__isDNS(line):
                    continue
                if self.__isCategory(line):
                    default_values["Category"] = self.__getCategory(line)
                    continue

                # else it's a racer with a place
                vars = line.split(self.__IN_DELIM)
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
    parser.add_argument('-r', dest="raceName", help="Name of the race")
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument("-v", action="store_true", help="Print verbose information about program process")
    args = parser.parse_args()
    
    if args.v:
        logger.setLevel(logging.DEBUG)

    reshaper = Reshaper(args.inFoldName, args.outFileName, args.raceName)
    reshaper.getFiles()
    reshaper.outputData()
