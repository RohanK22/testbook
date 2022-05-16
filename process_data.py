# TODO: Add eror flag on finding faulty data points
# TODO: Fix wrap around problem

import os
import sys
import datetime
import dateutil.parser as dparser # https://stackoverflow.com/questions/3276180/extracting-date-from-a-string-in-python
import re

# Print script start time and date. We might want to have a separate log file.
print("Script starting ", datetime.datetime.now())

# Get path to data folder as command line argument.
data_folder = sys.argv[1]

# Construct the path to other folders.
input_folder = os.path.join(data_folder, 'input')
output_folder = os.path.join(data_folder, 'output')
processed_folder = os.path.join(data_folder, 'processed')

if(os.path.isdir(data_folder)):
    print("Found data folder at ", data_folder)
else:
    print("Could not find data folder at ", data_folder)
    print("Usage: python3 process_data.py <path to data folder>")
    sys.exit(1)

if(os.path.isdir(input_folder)):
    print("Found Input folder at ", input_folder)
else:
    print("Could not find input folder within data folder. Creating...")
    os.mkdir(input_folder)
    print('Make sure to add files into the input folder for processing and run again.')
    sys.exit(1)

if(os.path.isdir(output_folder)):
    print("Found output folder at ", output_folder)
else:
    print("Could not find output folder within data folder. Creating...")
    os.mkdir(output_folder)

if(os.path.isdir(processed_folder)):
    print("Found processed folder at ", processed_folder)
else:
    print("Could not find processed folder within data folder. Creating...")
    os.mkdir(processed_folder)

# Check if there are any files in the input folder to process.  
inputFilesNames = os.listdir(input_folder)
nFilesToProcess = len(inputFilesNames)
if(nFilesToProcess == 0):
    print("No files in input folder. Exiting...")
    sys.exit(1)

print("Found ", nFilesToProcess," file(s) in input folder")

METADATA_REGEX = r'^\$\$\$(\w{12})\$(\w+)\$(\d+)'
DATETIME_REGEX_STRING = '([0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2][0-9]|3[0-1]) (?:2[0-3]|[01][0-9]):[0-5][0-9])'
DATAFEED_REGEX = r'(?P<date1>[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2][0-9]|3[0-1]) (?:2[0-3]|[01][0-9]):[0-5][0-9]),(?P<temp>\d+),(?P<rh>\d+)(?:,(?P<date2>[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2][0-9]|3[0-1]) (?:2[0-3]|[01][0-9]):[0-5][0-9])){0,1}(?:,(?P<minutes>\d+)){0,1}(?:,(?P<E>E)){0,1}'

for fileName in inputFilesNames:
    print("Processing file: ", fileName)

    # Construct the path to the input file.
    input_file = os.path.join(input_folder, fileName)

    # Meta data
    mac = ''
    desc = ''
    timeInterval = 0

    # Data
    data = []
    datapointsParsed = 0

    # Output file paths
    output_files = []
    try:
        inputFile = open(input_file, 'r')
        outputFile = None

        dateStr = ""
        lines = inputFile.readlines()
        
        for i in range(len(lines)):
            line = lines[i].strip()
            if(line.startswith('Date:')):
                parsedDateObj = dparser.parse(line, fuzzy=True) # TODO: Handle exception
                dateStr = parsedDateObj.strftime("%Y-%m-%d %H:%M")
                print(" Found date: ", dateStr)

            elif (line.startswith('$$$')):
                m = re.search(METADATA_REGEX, line) # TODO: Handle exception
                if(m):
                    print(" Found metadata: ", m.group(1), m.group(2), m.group(3))
                    mac = m.group(1)
                    desc = m.group(2)
                    timeInterval = int(m.group(3))

                    # Flush buffers
                    data.clear()
                    if outputFile and not outputFile.closed:
                        outputFile.close()
                        outputFile = None

                    # Look for file with name desc
                    output_file = os.path.join(output_folder, desc + '.csv')
                    output_files.append(output_file)
                    if(not os.path.isfile(output_file)):
                        print(" Creating file: ", output_file)
                        newOutputFile = True
                        outputFile = open(output_file, 'w')
                        # Write header
                        outputFile.write(mac + ',' + desc + ',' + str(timeInterval) + '\n')
                    else:
                        # Load Old data from file into data array
                        print(" Found file: ", output_file, " Loading data...")
                        outputFile = open(output_file, 'r')
                        data = outputFile.readlines()
                        outputFile.close()
                        data = data[1:] # Remove header
                        for i in range(len(data)):
                            data[i] = data[i].strip('\n ')
                        outputFile = open(output_file, 'a')
                    
                else:
                    print("Could not parse metadata: ", line)
            else:
                m = re.search(DATAFEED_REGEX, line) # TODO: Handle exception
                if(m):
                    # print("Found data: ", m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))
                    dataStr = ''
                    for s in m.groups():
                        if(s):
                            dataStr += s + ' '
                    dataStr = dataStr.strip()
                    dataStr = dataStr.replace(' ', ',')
                    if(dataStr not in data and outputFile): # If it is a unique data point add it to the list
                        data.append(dataStr)
                        outputFile.write(dataStr + '\n')
                        datapointsParsed += 1
        inputFile.close()
        if outputFile and not outputFile.closed:
            outputFile.close()
    except:
        print("Failed to process ", input_file, " Error: ", sys.exc_info())
        inputFile.close()
        if outputFile and not outputFile.closed:
            outputFile.close()
        sys.exit(1)
    
    print(" Found ", datapointsParsed, " new data points")
    print("Processed file ", input_file, " and wrote to files ", output_files)

    # Move the file to the processed folder
    try:
        os.rename(input_file, os.path.join(processed_folder, fileName))
        print('Moved ', input_file,' to processed folder')
    except:
        print('Faile to move file to processed folder. Error: ', sys.exc_info()[0])
    
    
