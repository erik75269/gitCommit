from __future__ import division
from subprocess import PIPE, Popen
from numpy import *
import sys
import numpy as np
from numpy import median
import time as sysTime
import datetime
import csv
import re
targetFolder = "cd ../CR-group-1/pdfbox/;"
totalFilesCmd = "find ./ -type f | wc -l"
authors = []
IssueIDs = []
newcommitInfo =[]
authorsInactive = []
totalCommits = 0
totalFilesCount = 0
def cmdline(command):
    # Init for cmdline operation
    process = Popen(
            args = command,
            stdout = PIPE,
            shell = True
            )
    return process.communicate()[0]
def targetIsGit():
    """Return true if targer folder is git folder, other wise return false"""
    cmd = targetFolder + 'git rev-parse --is-inside-work-tree'
    if cmdline(cmd)[:4] == "true":
        print "Can find git target folder, Analyzing..."
    else:
        print("Cannot find git target, exit the program")
        sys.exit();

def getAllBranchesName():
    """Return all branches of repository"""
    cmd = targetFolder + 'git branch -a'
    branchesName = []
    for char in cmdline(cmd):
        branchesName.append(char)
    branchesName = branchesName[:-2]
    branch = ''.join(branchesName).split('\n  ')
    return branch

def findIssueID():
    cmd = targetFolder + 'git log --before="2017-11-01" --name-status --reverse --all --date=iso --grep="PDFBOX-"'
    commits = []
    IssueID =[]
    newCommitandIDs = []
    for char in cmdline(cmd):
        commits.append(char)
    commits = ''.join(commits).split('commit ')

    # getALLissueID
    # print commits
    for i in xrange(len(commits)):
        match = re.findall('PDFBOX-\d+',commits[i])
        # print match
        for m in xrange(len(match)):
            IssueID.append(match[m])          
    IssueID = list (set(IssueID))
    IssueID.sort()
    for newIssueID in IssueID:
        
        newIssueIDObj = {
                    "IssueID":newIssueID,
                    "commit":[],
                    "stat":{
                      "M":0,
                      "D":0,
                      "A":0,
                    }
        }
        IssueIDs.append(newIssueIDObj) 
    
    for commit in commits:
            match = re.findall('PDFBOX-\d+',commit)
            for ID in IssueIDs:
                for i in xrange(len(match)):
                    if ID['IssueID'] == match[i]:
                        ID['commit'].append(commit[:7])
                        ID['commit'] = list(set((ID['commit'])))

def getChangedFilesTypeByCommit():

    def isFilesLine(line):
        if (line[0] == "D" or line[0] == "M" or line[0]== "A") and line[1] == "\t":
            return True
        else:
            return False
    def FileType(line):
        return line[0]
        
    #-------------------- Calculate the change file number ---------------------#
    def storeFilesTypesOfEachCommitInTypeObj(typeObj, fileType):
        if fileType == "M":
            typeObj['stat']['M'] = typeObj['stat']['M'] + 1
        elif fileType == "D":
            typeObj['stat']['D'] = typeObj['stat']['D'] + 1
        elif fileType == "A":
            typeObj['stat']['A'] = typeObj['stat']['A'] + 1
        else:
            print "FileType is error"
        return typeObj
        # return True

    cmd = targetFolder + 'git log --before="2017-11-01" --name-status --reverse --all --date=iso --grep="PDFBOX-"'
    commitNames = []
    global newcommitInfo
    for char in cmdline(cmd):
        commitNames.append(char)
    commitNames = ''.join(commitNames).split('commit ')
    for commit in commitNames:
        newCommitObj ={
                        "commit":commit[:7],
                        "stat":{
                           "M":0,
                           "D":0,
                           "A":0,
                        }
                    }
        newcommitInfo.append(newCommitObj)
        for eachLine in commit.split('\n'):
            try:
                
                if isFilesLine(eachLine) == True:
                    fileType = FileType(eachLine)
                    newCommitObj =storeFilesTypesOfEachCommitInTypeObj(newCommitObj, fileType)

            except IndexError:
                    eachLine

    # print newcommitInfo               
def getStat():
        
    for ID in IssueIDs:
        mCount = 0
        for i in range(len(ID['commit'])):
            for eachCommit in newcommitInfo:
                if eachCommit['commit'] == ID['commit'][i]:
                    mCount = mCount + int(eachCommit['stat']['A'])
        ID['stat']['A'] = mCount

    for ID in IssueIDs:
        mCount = 0
        for i in range(len(ID['commit'])):
            for eachCommit in newcommitInfo:
                if eachCommit['commit'] == ID['commit'][i]:
                    mCount = mCount + int(eachCommit['stat']['M'])
        ID['stat']['M'] = mCount

    for ID in IssueIDs:
        mCount = 0
        for i in range(len(ID['commit'])):
            for eachCommit in newcommitInfo:
                if eachCommit['commit'] == ID['commit'][i]:
                    mCount = mCount + int(eachCommit['stat']['D'])
        ID['stat']['D'] = mCount

    print IssueIDs

def writeTocsv():
    with open('resultfPDF.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='excel')
        csvwriter.writerow(['Issue ID', 'Commits','Added', 'Modified', 'Deleted'])
        for ID in IssueIDs:
            csvwriter.writerow(
            [ID['IssueID'], 
            ID['commit'],
            ID['stat']['A'],
            ID['stat']['M'],
            ID['stat']['D'],
            ])

def main():
    
    targetIsGit()
    findIssueID()
    getChangedFilesTypeByCommit()
    getStat()
    writeTocsv()
# This module is being run standalone.
if __name__ == "__main__": main()
