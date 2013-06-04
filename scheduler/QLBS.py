'''
Created on Jun 4, 2013

@author: sivabalan
'''
'''
Created on May 27, 2013

@author: sivabalan
'''
from proj.tasks import add,add1
from celery.task.control import inspect
from threading import *
from celery import chord
import json,sys,time,cPickle
from random import randint
from proj.celery import celery
import Queue,threading, thread

from celery.events import EventReceiver
from celery.messaging import establish_connection
import sys,redis,datetime

class my_monitor(Thread):      
        def __init__(self,queuelist):
                Thread.__init__(self) 
                self.app = celery
                self.state = self.app.events.State()
                self.cond = Condition()
                self.task_dict = {}
                self.q = {}
                #self.r_server =  redis.Redis("128.111.55.219")
                self.execTime = 0
                self.count = 0
                self.tasktypes = {"add","add1","add2"}
                self.queuecounts= {}
                self.tasktimes = {}
                self.taskexectimes={}
                self.taskidtypedict = {}
                for item in queuelist:
                    self.q[item] = 0
                    self.queuecounts[item] = 0
                #print "Task times"
                for item in self.tasktypes:
                    self.tasktimes[item] = self.r_server.hget("celery-totalexectime",item)
                    self.taskexectimes[item] = self.r_server.hget("celery-totalexectime",item)
                 #   print item," ",self.tasktimes[item]
                
                    
        def getTaskType(self,task):
              return task.type.name[task.type.name.rfind(".")+1:]
                
        def announce_sent_tasks(self,event): #to retrieve mapping between task id and queue
                self.state.event(event)
                stask_id = event['uuid']
                squeue = event['queue']
                self.cond.acquire()
                self.task_dict[stask_id] = squeue
                #self.cond.acquire()
                self.queuecounts[squeue] = self.queuecounts[squeue] + 1
                self.cond.release()
                print "No of tasks in ",squeue," = ",self.queuecounts[squeue]," after send event"
                print stask_id , " sent to ",self.task_dict[stask_id]  #append key,value to dictionary, key is task id and value is queue name i.e priority_high or default
                #print ('QUEUE: %s'%(squeue))
                #print ('TASK ID: %s'%(stask_id)) 
                
        def announce_succeeded_tasks(self,event):
                self.state.event(event)
                task_id = event['uuid']
                runtime = event['runtime']
                print " ----------------------------------------------------------------- "
                print('TASK EXECUTED-TASK ID: %s'%(task_id))
                queue_value = self.task_dict.get(task_id) # for the executed task look up the queue value
                print task_id,queue_value
                tqueue = self.task_dict[task_id]
                print self.taskidtypedict[task_id]
                
                tasktype = self.taskidtypedict[task_id]
                #print "approx time ",self.tasktimes[tasktype]
               
                self.taskexectimes[tasktype] = (float(self.taskexectimes[tasktype] )+ runtime)/2
#                print "new time",self.tasktimes[tasktype] = (self.tasktimes[tasktype] + runtime)/2
                self.cond.acquire()
                print "Queue length ", self.q[tqueue], " ",tqueue
                self.q[tqueue] = self.q[tqueue]-float(self.tasktimes[tasktype])
                self.queuecounts[tqueue] = self.queuecounts[tqueue] - 1
                print "No of tasks in ",tqueue," = ",self.queuecounts[tqueue]," after receiving Success event"
                print "Queue length ", self.q[tqueue], " ",tqueue
                self.cond.release()
                print " ----------------------------------------------------------------- "
                #temp = self.r_server.get("Celery-Total-ExecTime")
                #temp = runtime + float(temp)
                #self.r_server.set("Celery-Total-ExecTime",temp)
                self.count = self.count +1
                b = datetime.datetime.now()
                c = b - self.a
                print c
                print divmod(c.days * 86400 + c.seconds, 60)," for ",self.count," tasks"
                if self.count == 500:
                    for item in self.tasktypes:
                        self.r_server.hset("celery-totalexectime", item, self.taskexectimes[item]) 
                
                #if (queue_value):
                        #q.put(queue_value)        

        def run(self):       
                self.a = datetime.datetime.now()         
                while True:
                        try:
                                with self.app.connection() as connection:
                                        recv = self.app.events.Receiver(connection, handlers={
                            # 'task-started': on_event,                                         
                                 'task-sent': self.announce_sent_tasks,
                                 'task-succeeded': self.announce_succeeded_tasks,
                    })
                                        recv.capture(limit=None, timeout=None, wakeup=True)
                        except (KeyboardInterrupt, SystemExit):
                                print "EXCEPTION KEYBOARD INTERRUPT"
                                self.app.close()
                        sys.exit()        
                        
        def getMinQueue(self):   
            min = sys.maxint
            minQueue = ''
          #  self.cond.acquire()
            queuelengths = ''
            queues = ''
            for k in self.q.keys():
                queues = k,' ',queues
                v = self.q[k]
                queuelengths = v," ",queuelengths
                if v < min:
                    min = v
                    minQueue = k
           # self.cond.release() 
            #print min
            print queues
            print 'Queue lengths ',queuelengths
            print minQueue
            return minQueue
        
        def test(self,user,tasklist):
                count = 1
                self.starttime = datetime.datetime.now()  
                for entry in tasklist:   # execute some tasks of the format add.s(x,y)
                        task = entry
                        minQ = self.getMinQueue()
                        print "Assigning ",task," to ",minQ
                        result = task.apply_async(queue=minQ)
                        self.cond.acquire()
                        tasktime = self.tasktimes[self.getTaskType(task)]
                        self.q[minQ] = self.q[minQ]+float(tasktime)
                        self.cond.release()
                        print result
                        self.task_dict[result] = minQ
                        self.taskidtypedict[result] = self.getTaskType(task)
                        count = count +1
                            
                self.endtime = datetime.datetime.now()
                print "Scheduling time ",self.endtime-self.starttime
                self.r_server.set("celery-scheduling-time",self.endtime-self.starttime)
                           
                while(True) : pass     
        
def main():
    
        FILE = open("tasks1.txt", 'r')
        taskslist = cPickle.load(FILE)
        FILE.close()
        print "Task list"
        print taskslist
        t = my_monitor(['w48','w49','w50']) #instance for the my_monitor class
        t.daemon = True
        t.start()        
        t.test("client1",taskslist)

if __name__ == "__main__":
        main()