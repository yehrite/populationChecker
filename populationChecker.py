#!/usr/bin/env python3
"""
Author: Dylan Hull
Description: Course capstone project
"""
print('Name: Dylan Hull')
import argparse, requests, bs4, subprocess, json

def getNextFileInQueue():
    varURL = 'http://www.py.land/population_check_queue'
    varThreshold = 60
    response = requests.get(varURL)
    dictHeaders = response.headers
    if 'LAST_REFRESHED_MINS' not in dictHeaders or int(dictHeaders['LAST_REFRESHED_MINS']) > varThreshold:
        print("'Population Check Queue' scheduler running? Have the 'PCQ' Manager check and refresh before running again!")
        return ""
    else:
        myHTML = bs4.BeautifulSoup(response.text,features="html.parser")
        lrmInt = int(dictHeaders['LAST_REFRESHED_MINS'])
        listLineObject = myHTML.select('li')
        if listLineObject:
            lineObjectStr = myHTML.select('li')[0].text
            return lineObjectStr, lrmInt
        else:
            return ""

def determineOutputFileName(varInputFile, varOutputFile):
    varOutputFileName = ""
    if varOutputFile:
        varOutputFileName = varOutputFile + ".out"
    else:
        varOutputFileName = varInputFile.replace('.txt','.out')
    return varOutputFileName

def checkFileExistence(varInputFile):
    directoryFiles = subprocess.run("ls", shell=True, stdout=subprocess.PIPE)
    listDirectoryFiles = directoryFiles.stdout.decode().split('\n')
    matching = 0
    for item in listDirectoryFiles:
        if varInputFile == item:
            matching += 1
        else:
            pass
    if matching >= 1:
        return True
    else:
        return False
        
    print(listDirectoryFiles)

def checkPopulation(varInputFile, varOutputFile):
    baseURL = 'http://www.py.land/population'
    URLparams = {"drilldowns": "State", "measures": "Population", "year": "latest"}
    responseStr = requests.get(baseURL, params=URLparams)
    jsonDict = responseStr.json()
    stateDataList = jsonDict['data']
    try:
        # Read from the input file and write to the output file.
        with open(varInputFile, 'r') as file:
            lines = file.readlines()
        with open(varOutputFile, 'w') as outFile:
            for item in stateDataList:
                # Break down each line of the reference file.
                valuesList = list(item.values())
                SID = valuesList[0]
                Pop = int(valuesList[2])
                sName = valuesList[4]
                for line in lines:
                    # Break down each line of the input file.
                    lineList = line.strip().split('\n')
                    lineList2 = lineList[0].strip().split(',')
                    # Identify lines with matching State and non-matching population.
                    if lineList2[0] == SID and int(lineList2[1]) != Pop:
                        outFile.write(f"{lineList2[0]},{sName},{Pop}\n")
        return True
    except:
        return False

def main():
    myParser = argparse.ArgumentParser(description='Population scrubber')
    myParser.add_argument('-o', '--outputFileName', dest='varOutputFileNameStr', type=str, help='Optional: Name of file (without extention) to return to the user.')
    myArgs = myParser.parse_args()

    lineObjectStr, lrmInt = getNextFileInQueue()
    if lineObjectStr:
        print(f"File to process: {lineObjectStr}")
    else:
        print(f"File to process:\nNo Files to process.")

    varDeterminedFilename = determineOutputFileName(lineObjectStr, myArgs.varOutputFileNameStr)
    print(f"Output file: {varDeterminedFilename}")

    print(f"Previous output overwritten? {checkFileExistence(varDeterminedFilename)}")

    fileProcessed = checkPopulation(lineObjectStr, varDeterminedFilename)
    print(f"File processed: {fileProcessed}")

if __name__ == "__main__":
    main()