#!/usr/bin/python

from __future__ import division
import sys, collections
from collections import defaultdict
from operator import itemgetter
from collections import deque
import operator
import numbers
import os.path

def initTimes(responseTimes):
   for i in range(len(responseTimes)): 
      temp = [i, -1]
      responseTimes[i] = temp

#### SHORTEST REMAINING JOB NEXT ####
def srjn(jobs):
   totalRunTime = addRunTimes(jobs)
   time = 0
   queue = []
   waitTimes = []
   turnaroundTimes = []
   averages = [] 
   mainqueue = deque()
   ndx = 0
   flag = 0
   responseTimes = [] 
   globalNdx = 0

   for x in jobs:
      mainqueue.append(jobs[x])

   responseTimes = [0]*len(mainqueue)
   initTimes(responseTimes)

   turnaroundTimes = [0]*len(mainqueue)
   initTimes(turnaroundTimes)

   largestBurstValue = mainqueue[len(mainqueue) - 1][1]
   while (time <= totalRunTime + 50 or time <= largestBurstValue):
      if len(mainqueue) > 0:
         numDone = 0
         for i in mainqueue:    
            currentWait = []
            tempQueue = []
            tempResponse = []
            if i[1] <= time:
               currentWait.append(ndx)
               currentWait.append(time - i[1])
               waitTimes.append(currentWait)
               tempQueue.append(ndx)
               tempQueue.append(i)
               queue.append(tempQueue)
               numDone = numDone + 1
               ndx+=1
         for j in range(numDone):
            mainqueue.popleft()
      queue.sort(key=lambda x: x[1][0])

      if len(queue) > 0:
         currentIndex = queue.pop(0)   
         globalNdx = currentIndex[0] 

         if responseTimes[globalNdx][1] == -1:
            responseTimes[globalNdx][1] = float(time + 1 - currentIndex[1][1])

         for i in queue:
            for j in waitTimes:
               if j[0] == i[0]:
                  j[1] += 1
         currentIndex[1][0] -= 1
      
         time += 1
         tempTurnaround = []
         if currentIndex[1][0] == 0:
            if turnaroundTimes[globalNdx][1] == -1:
               turnaroundTimes[globalNdx][1] = float(time - currentIndex[1][1])
               currentIndex = None
         else:
            queue.insert(0, currentIndex)
         
      else:
         time += 1

   averages = getPreemptiveAverages(waitTimes, responseTimes, turnaroundTimes, jobs)
   preemptiveResults(averages, waitTimes, responseTimes, turnaroundTimes, jobs)

#### ROUND ROBIN ####
def rr(jobs, quantum):
   time = 0
   externalTime = 0
   totalRunTime = addRunTimes(jobs)
   mainqueue = deque()
   waitTimes = []
   turnaroundTimes = []
   responseTimes = []
   current = None
   ndx = 0
   averages = []
   queue = deque()
   quantum = int(quantum)
   flag = 0

   for x in jobs:
      mainqueue.append(jobs[x])

   largestBurstValue = mainqueue[len(mainqueue) - 1][1]
   while time <= totalRunTime or time <= largestBurstValue:
      tempResponse = []
      if len(mainqueue) > 0:
         numDone = 0
         for i in mainqueue:
            if current != None and i[1] == time:
               tempQueue = []
               tempQueue.append(ndx)
               #tempQueue.append(i)
               tempQueue.append(current[1])
               queue.append(tempQueue)
               current = None
            if i[1] <= time:
               currentWait = []
               currentWait.append(ndx)
               currentWait.append(time - i[1])
               waitTimes.append(currentWait)
               
               tempQueue = []
               tempQueue.append(ndx)
               tempQueue.append(i)
               queue.append(tempQueue)
               ndx += 1
               numDone += 1
         for j in range(numDone):
            mainqueue.popleft() 
      if current != None:
         queue.append(current)

      if len(queue) > 0:
         current = queue.popleft()
        
         if current[1][0] >= quantum:
            externalTime = quantum
         else:
            externalTime = current[1][0]
         for i in queue:
            for j in waitTimes:
               if j[0] == i[0]:
                  j[1] += externalTime
         current[1][0] -= externalTime 
                
         for y in range(len(responseTimes)):
            if responseTimes[y] == ndx:
               flag = 1
         if flag == 0:
            tempResponse = []
            tempResponse.append(ndx)
            tempResponse.append(float(time - current[1][1] + 1))
            responseTimes.append(tempResponse)    

         time += externalTime
         tempTurnaround = []
         if current[1][0] == 0:
            tempTurnaround.append(current[0])
            tempTurnaround.append(float(time - current[1][1]))
            turnaroundTimes.append(tempTurnaround)
            current = None
      else:
         time = time + 1

   averages = getPreemptiveAverages(waitTimes, responseTimes, turnaroundTimes, jobs)
   preemptiveResults(averages, waitTimes, responseTimes, turnaroundTimes, jobs)

#### FIRST IN FIRST OUT ####
def fifo(jobs):
   time = 0
   index = 0
   serviceTimes = []
   averages = []
   totalRunTime = addRunTimes(jobs)
   serviceTimes.append(0)

   while (time != totalRunTime):
      time = time + jobs[index][0]
      serviceTimes.append(time)
      index = index + 1
   
   waitTimes = fifoWaitTimes(serviceTimes, jobs)
   responseTimes = fifoResponseTimes(waitTimes)
   turnaroundTimes = fifoTurnaroundTimes(waitTimes, jobs)
   averages = getAverages(waitTimes, responseTimes, turnaroundTimes, jobs)
   printResults(averages, waitTimes, responseTimes, turnaroundTimes, jobs)

def getPreemptiveAverages(waitTimes, responseTimes, turnaroundTimes, jobs):
   totalWaitTime = 0
   totalResponseTime = 0
   totalTurnaroundTime = 0
   averages = []
   for x in range(0, len(waitTimes)):
      totalWaitTime += waitTimes[x][1]    
      totalResponseTime += responseTimes[x][1]
      totalTurnaroundTime += turnaroundTimes[x][1]
   averages.append(float(totalResponseTime/len(jobs)))
   averages.append(float(totalTurnaroundTime/len(jobs)))
   averages.append(float(totalWaitTime/len(jobs)))
   return averages

def getAverages(waitTimes, responseTimes, turnaroundTimes, jobs):
   totalWaitTime = 0
   totalResponseTime = 0
   totalTurnaroundTime = 0
   averages = []
   for x in range(0, len(waitTimes)):
      totalWaitTime += waitTimes[x]
      totalResponseTime += responseTimes[x]
      totalTurnaroundTime += turnaroundTimes[x]
   averages.append(float(totalResponseTime/len(jobs)))
   averages.append(float(totalTurnaroundTime/len(jobs)))
   averages.append(float(totalWaitTime/len(jobs)))
   return averages

def fifoWaitTimes(serviceTimes, jobs):
   waitTimes = []
   for x in range(0, len(jobs)):
      waitTimes.append(float(serviceTimes[x] - jobs[x][1]))
   return waitTimes

def fifoResponseTimes(waitTimes):
   responseTimes = []
   for x in range(0, len(waitTimes)):
      responseTimes.append(float(waitTimes[x] + 1))
   return responseTimes

def fifoTurnaroundTimes(waitTimes, jobs):
   turnaroundTimes = []
   for x in range(0, len(waitTimes)):
      turnaroundTimes.append(float(waitTimes[x] + jobs[x][0]))
   return turnaroundTimes
  
def preemptiveResults(averages, waitTimes, responseTimes, turnaroundTimes, jobs):
   for i in range(len(turnaroundTimes)):
      print "Job " + str(i) + " -- Response: " + str(responseTimes[i][1]) +  \
            "  Turnaround " + str(turnaroundTimes[i][1]) + "  Wait " + \
            str(waitTimes[i][1])
   print ("Average -- Response: " + str(averages[0]) + "  Turnaround " + \
          str(averages[1]) + "  Wait " + str(averages[2]))

def printResults(averages, waitTimes, responseTimes, turnaroundTimes, jobs):
   for x in jobs:
      print "Job " + str(x) + " -- Response: " + str(responseTimes[x]) + \
            "  Turnaround " + str(turnaroundTimes[x]) + "  Wait " + \
            str(waitTimes[x])
   print ("Average -- Response: " + str(averages[0]) + "  Turnaround " + \
          str(averages[1]) + "  Wait " + str(averages[2]))

    

def addRunTimes(jobs):
   totalRunTime = 0
   for x in range(0, len(jobs)):
      totalRunTime = totalRunTime + jobs[x][0]
   return totalRunTime

def main(argv):
   jobs = []
   numArgs = 5;

   #### PARSING ####
   if len(sys.argv) < 6: 
      print("Usage: schedSim.py <job-file.txt> -p <ALGORITHM> -q <QUANTUM>")
      sys.exit()
   
   jobFile = sys.argv[1]
   for i, arg in enumerate(sys.argv):
      if arg == "-p":
         algorithm = sys.argv[i + 1]
      elif arg == "-q":
         quantum = sys.argv[i + 1]

   if jobFile[-4:] != ".txt":
      print("Input file should be txt")
      sys.exit()
   if algorithm != "SRJN" and algorithm != "FIFO" and algorithm != "RR":
      print(algorithm)
      print("Wrong algorithm")
      sys.exit()
   if quantum.isdigit() == False:
      print("Quantum has to be a valid integer.")
      sys.exit()
   if os.path.isfile(jobFile) == False:  
      print("File does not exist.")
      sys.exit()

   #### READING FROM FILE AND POPULATING DICTIONARY ####

   with open(jobFile) as file:
      for i, line in enumerate(file):
         spl = line.split()
         spl = map(int, spl)
         if len(spl) == 2:
           jobs.append(spl)
  
   jobs.sort(key=lambda x: x[1])

   jobDict = {}

   for i in range(0, len(jobs)):
     jobDict[i] = jobs[i]

   if algorithm == "SRJN":
      srjn(jobDict)

   if algorithm == "FIFO":
      fifo(jobDict)

   if algorithm == "RR":
      rr(jobDict, quantum)
   
if __name__ == "__main__":
   main(sys.argv[1:])
  
