'''
Created on Jun 4, 2013

@author: sivabalan
'''

import redis,datetime
from scheduler.Scheduler import Scheduler


class FCFSScheduler( Scheduler ):
    def __init__(self,queuelist):
         Scheduler.__init__(self,queuelist)
        
    def assignTasks(self,user,tasklist):
        self.starttime = datetime.datetime.now()  
        for item in tasklist:
            curQueue = self.queuelist[self.count%self.totalworkers]
            print "Assigning ",item," to ",curQueue
            result = item.apply_async(queue=curQueue)
            print result
            self.count += 1
        self.endtime = datetime.datetime.now()
        print "Scheduling time ",self.endtime-self.starttime
        self.r_server.set("celery-scheduling-time",self.endtime-self.starttime)