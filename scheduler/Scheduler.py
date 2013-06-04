'''
Created on Jun 4, 2013

@author: sivabalan
'''

from celery.task.control import inspect
from proj.tasks import add,mul,xsum
from proj.celery import celery
from sets import Set
from celery import chord,group,chain
import logging
import redis

class Scheduler():
    count = 0
    
    def __init__(self,queuelist):
            Scheduler.r_server =  redis.Redis("128.111.55.219")
            Scheduler.totalworkers = 0
            Scheduler.queuelist = queuelist
         #   Scheduler.workernodes = self.getworkerNodes()
          #  print Scheduler.workernodes
            Scheduler.totalworkers = len(self.queuelist)
          #  Scheduler.Schedulername = name
            Scheduler.r_server.set("Celery-Total-ExecTime",0)
                
    def getPid(self,workernode):
        i = inspect()
        temp = i.stats()
        for k,v in temp.iteritems():
            if k == workernode:
                print "worker node :: ",k
                for a,b in v.iteritems():
                    if a == "pool":
                        #print b
                        for c,d in b.iteritems():
                            if c == "processes":
                                #print d
                                return d
                            
    def getworkerNodes(self):
        i = inspect()
        temp = i.stats()
        workernodes = []
        for k,v in temp.iteritems():
            workernodes.append(k)
        return workernodes
            
    def printTasks(self,tasks):
        for item in tasks:
             print "-----------------------------"
             print ""
             for a,b in item.iteritems():          
              if a == "request":
                print "Request :"
                for c,d in b.iteritems():
                    print c," -- ",d
              else:
                print a," ",b
    
    
    
    def checkStatus(self,task_id):
        '''
        Method takes task_id as input and returns the result of the celery task
        '''
        logging.info("checkStatus inside method with params %s", str(task_id))
        result = {}
        try:
            from celery.result import AsyncResult
            res = AsyncResult(task_id)
            logging.debug("checkStatus: result returned for the taskid = {0} is {1}".format(task_id, str(res)))
            result['result'] = res.result
            result['state'] = res.status
            if res.status == "PROGRESS":
                print 'Task in progress'
                print 'Current %d' % result['current']
                print 'Total %d' % result['total']
                result['result'] = None
            elif res.status == "SUCCESS":
                result['result'] = res.result
                #print "success"
            elif res.status == "FAILURE":
                result['result'] = res.result 
                #print "failure"
            
        except Exception, e:
            logging.debug("checkStatus error : %s", str(e))
            print "Exception thrown "
            result['state'] = "FAILURE"
            result['result'] = str(e)
        logging.debug("checkStatus : Exiting with result %s", str(res))
        return result
    
    def getTasks(self):
        return Scheduler.r_server.keys("celery-task-meta-*")
  
    def assignTasks(self,user,tasklist):
        raise NotImplementedError( "Should have implemented this" )  
    
    def getAllWorkerTasks(self):        
        for item in self.workernodes:
            print item
            print Scheduler.r_server.lrange("celery-workertask-map-"+item, 0,-1)        
    
    def getAllUserTasks(self):
        userslist = Scheduler.r_server.keys("celery-usertaskworker-map-*")
        for user in userslist:
            print  user.replace("celery-usertaskworker-map-","")
            taskworkermap = Scheduler.r_server.hgetall(user)
            for k,v in taskworkermap.iteritems():
                print k," assigned to ",v
            
    def getAllSucceededTasks(self):
        print "All Succeeded Tasks::"
        taskslist = Scheduler.r_server.keys("celery-taskSucceeded-*")
        f = open('sampleData.json', 'w+')
        f.write("{\n")
        for item in taskslist:
            print  "     ",item.replace("celery-taskSucceeded-","")
            f.write("{\n",item.replace("celery-taskSucceeded-",""))
            f.write("\n")
            taskmap = Scheduler.r_server.hgetall(item)
            for k,v in taskmap.iteritems():
                print "         ",k," ",v
                f.write("  %s:%s\n" % (k,v))
        f.write("}\n")
        f.close()
                
    def getAllSuccessfulTasksSorted(self):
        print "Sorted Successful Tasks :: "
        print Scheduler.r_server.sort("taskslist",by='celery-taskSucceeded-*->runtime', get='celery-taskSucceeded-*->#')
        #print TaskDetails.r_server.sort("taskslist",by='celery-taskSucceeded-*->runtime')
  



