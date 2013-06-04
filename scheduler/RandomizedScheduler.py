'''
Created on Jun 4, 2013

@author: sivabalan
'''
import redis
import random,datetime
from scheduler.Scheduler import Scheduler

class RandomizedScheduler( Scheduler ):
        
   def __init__(self,queuelist):
        Scheduler.__init__(self,queuelist)
        
   def assignTasks(self,user,tasklist):
        self.starttime = datetime.datetime.now()  
        for item in tasklist:
            curQueue = self.queuelist[random.randint(1, self.totalworkers)-1]
            print "Assigning ",item," to ",curQueue
            result = item.apply_async(queue=curQueue)
            print result
            Scheduler.count += 1
        self.endtime = datetime.datetime.now()
        print "Scheduling time ",self.endtime-self.starttime
        self.r_server.set("celery-scheduling-time",self.endtime-self.starttime)
