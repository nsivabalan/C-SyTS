'''
Created on Jun 4, 2013

@author: sivabalan
'''

from proj.tasks import add1,add,add2
from celery.task.control import inspect
from celery import chord
import json,sys
from random import randint
from scheduler.Scheduler import Scheduler
from scheduler.FCFSScheduler import FCFSScheduler
from scheduler.RandomizedScheduler import RandomizedScheduler
import cPickle

def main():   
    
    loop = []      
#     count1 = 0
#     count2 = 0
         #code to generate 300 tasks of random types
#     for x in xrange(300):
#         opertn = randint(0,2)
#         if opertn == 0:
#             temp = add.s((randint(0,100)),(randint(0,100)))
#             print temp
#             count = count + 1
#             count1 = count1 + 1
#             loop.append(temp)
#         elif opertn == 1:
#             temp = add1.s((randint(0,100)),(randint(0,100)))
#             print temp
#             count = count + 1
#             count2 = count2 + 1
#             loop.append(temp)
#         else:
#             temp = add2.s((randint(0,100)),(randint(0,100)))
#             print temp
#             loop.append(temp)

#         print " add ",count1," add1 ",count2
    # code to generate 300 tasks of same type 
    count1 = 0
    for x in xrange(300):
              temp = add.s((randint(0,100)),(randint(0,100)))
              print temp
              count1 = count1+1
              loop.append(temp) 
                 
    FILE = open("tasks1.txt", 'w')
    cPickle.dump(loop, FILE)
    FILE.close()
   
    FILE = open("tasks1.txt", 'r')
    taskslist = cPickle.load(FILE)
    FILE.close()
    print "Task list"
    print taskslist
    
    schedulertype = sys.argv[0]
  #  print "total add tasks ",count1
    if schedulertype == "FCFS":
         schedulerObj = FCFSScheduler(["wnode1","wnode2","wnode3"])
    else:
         schedulerObj = RandomizedScheduler(["wnode1","wnode2","wnode3"])
    schedulerObj.assignTasks("client1",taskslist)
                
if __name__ == "__main__":
    main()
