import os
from string import Template

SCHEMA_FLAT = ["Category", "Place", "Bib", "Name", "Team name", "Age", "Year of birth", "Time"]
SCHEMA_RESHAPE = ["Lap", "Lap time"]
DEFAULT_CATEGORY = "Cat 1/2 Men"
DEFAULT_VALUE = "-"

IN_DELIM = "\t"
OUT_DELIM = ","

def main():
    file_list = getFiles()
    with open("parsed_results.csv", "w") as outF:
        writeHeader(outF)
        for file in file_list:
            processFile(file, outF)

def getFiles():
    files = []
    for test in os.listdir("./"):
        if not os.path.isfile(test):
            continue
        if test[-4:] != ".txt":
            continue
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
    main()