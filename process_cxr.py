"""
The format of the csv appears to be category, last name, first name, bib number, chip number, Start Time, [lap times], End Time
"""

import argparse
import logging
import sys

class Reshaper:
    def __init__(self, inFileName, outFileName, raceName =""):
        self.__logger = logging.getLogger(__name__)
        self.__inFileName = inFileName
        self.__outFileName = outFileName
        
        self.__SCHEMA_FLAT = ["Category", "Name", "Bib", "Chip", "Start Time", "End Time"]
        self.__SCHEMA_RESHAPE = ["Lap", "Lap time"]
        
        self.__IN_DELIM = ","
        self.__OUT_DELIM=","

    def reshapeData(self):
        with open(self.__inFileName, "r") as inF:
            self.__logger.info("Loading " + self.__inFileName)
            with open(self.__outFileName, "w") as outF:
                self.__logger.info("Writing to " + self.__outFileName)
                self.__writeHeader(outF)
                for line in inF:
                    flatData = {}
                    row = line.split(self.__IN_DELIM)
                    
                    for col in self.__SCHEMA_FLAT:
                        flatData[col] = self.__getData(col, row).strip()
                    
                    laps = self.__getLaps(row)
                    
                    self.__writeReshapedData(outF,flatData, laps)

    def __writeHeader(self, outF):
        outF.write(self.__OUT_DELIM.join(self.__SCHEMA_FLAT))
        outF.write(self.__OUT_DELIM)
        outF.write(self.__OUT_DELIM.join(self.__SCHEMA_RESHAPE))
        outF.write("\n")

    def __getData(self, col, row):
        if col == "Category":
            return row[0]
        if col == "Name":
            return row[2] + " " + row[1]
        if col == "Bib":
            return row[3]
        if col == "Chip":
            return row[4]
        if col == "Start Time":
            return row[5]
        if col == "End Time":
            return row[-1]
        self.__logger.error("Column '" + col + "' not present in row " + str(row))

    def __getLaps(self, row):
        return row[6:-1]

    def __writeReshapedData(self, outF, flatData, laps):
        for lap, time in enumerate(laps):
            for col in self.__SCHEMA_FLAT:
                outF.write(flatData[col])
                outF.write(self.__OUT_DELIM)
            outF.write(str(lap+1))
            outF.write(self.__OUT_DELIM)
            outF.write(time)
            outF.write("\n")

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    
    parser = argparse.ArgumentParser(description="Process Cross Revolution lap data into a single Tableau-readable\
    file")
    parser.add_argument('inFileName', metavar='inputFile', help='Path to the file containing the lap times')
    parser.add_argument('outFileName', metavar='outputFile', help="Path/name of the csv file to be created\
    for feeding into Tableau")
    parser.add_argument('-r', dest="raceName", help="Name of the race")
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument("-v", action="store_true", help="Print verbose information about program process")
    args = parser.parse_args()
    
    if args.v:
        logger.setLevel(logging.DEBUG)
    
    reshaper = Reshaper(args.inFileName, args.outFileName, args.raceName)
    reshaper.reshapeData()