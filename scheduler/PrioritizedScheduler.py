'''
Created on Jun 4, 2013

@author: sivabalan
'''


from proj.tasks import add,add1,add2
from celery.task.control import inspect
from threading import *
from celery import chord
import json,sys,time,random,cPickle
from random import randint
from proj.celery import celery
import Queue,threading, thread
import datetime

from celery.events import EventReceiver
from celery.messaging import establish_connection
#from kombu import Connection as BrokerConnection
import sys
import redis

class my_monitor(Thread):      
        def __init__(self,held_taskq,highq,lowq,cond):
                Thread.__init__(self)
                my_monitor.r_server =  redis.Redis("128.111.55.219")
                self.app = celery
                self.state = self.app.events.State()
                self.task_dict = {}
                self.hp_ctrsz = 0
                self.def_ctrsz = 0
                self.def_sla = 40
                self.hp_sla = 60
                self.highq = highq
                self.lowq = lowq
                self.held_ctr = 1
                self.cond = cond
                self.held_taskq = held_taskq
                self.tempheldqtask  = ""
                self.isheldqtaskavailable = False
                self.totalExecTime = 0
                self.count = 0
                self.tasktimes = {"add":10,"add1":30,"add2":60}
                self.taskexectimes = {"add":10,"add1":30,"add2":60}
                self.taskidtypedict ={}
        
        def announce_sent_tasks(self,event): #to retrieve mapping between task id and queue
                self.state.event(event)
                stask_id = event['uuid']
                squeue = event['queue']
                self.task_dict[stask_id] = squeue #append key,value to dictionary, key is task id and value is queue name i.e priority_high or default
                
        def announce_succeeded_tasks(self,event):
                self.state.event(event)
                self.test
                task_id = event['uuid']
                runtime = event['runtime']
                print('TASK EXECUTED-TASK ID: %s'%(task_id))
                queue_value = self.task_dict.get(task_id) # for the executed task look up the queue value
                print task_id,queue_value
                tasktype = self.taskidtypedict[task_id]
                self.cond.acquire()
                self.taskexectimes[tasktype] = (self.taskexectimes[tasktype] + runtime)/2
                if (queue_value == self.highq):
                    self.hp_ctrsz = self.hp_ctrsz - self.tasktimes[tasktype]
                elif (queue_value == self.lowq):
                        self.def_ctrsz = self.def_ctrsz - self.tasktimes[tasktype]
                print "Queue Size :: Default Queue size ",self.def_ctrsz,", High Priority Queue size ",self.hp_ctrsz
                self.cond.release()
                self.count = self.count +1
                self.b = datetime.datetime.now()
                self.c = self.b - self.a
                print self.c
                print "Total time taken :: ",self.tasktimes," for ",self.count," tasks"
                
        def run(self):
                self.a = datetime.datetime.now()                
                while True:
                        try:
                                with self.app.connection() as connection:
                                        recv = self.app.events.Receiver(connection, handlers={  
                                 'task-sent': self.announce_sent_tasks,
                                 'task-succeeded': self.announce_succeeded_tasks,
                    })
                                        recv.capture(limit=None, timeout=None, wakeup=True)
                        except (KeyboardInterrupt, SystemExit):
                                print "EXCEPTION KEYBOARD INTERRUPT"
                        sys.exit()        
        
        def test(self):
                count = 1
                while (True):
                        if self.isheldqtaskavailable == True:
                                task_set = self.tempheldqtask
                        else:
                                task_set = self.held_taskq.get()
                        #print task_set
                        self.tempheldqtask = task_set
                        self.isheldqtaskavailable = False
                        flag = False
                        task = task_set[0]
                        priority = task_set[1]
                        if (priority == 0): 
                                if (self.hp_ctrsz <= self.hp_sla) :
                                        res = task.apply_async(queue=self.highq)
                                        print "Task no ",count," ",task," ",res," assigned to ",self.highq
                                        tasktype = task.type.name[task.type.name.rfind(".")+1:]                                       
                                        self.taskidtypedict[res] = tasktype
                                        self.isheldqtaskavailable == False
                                        flag = True     
                                        self.cond.acquire()                                   
                                        self.hp_ctrsz = self.hp_ctrsz + self.tasktimes[tasktype]
                                        self.cond.release()
                                elif (self.def_ctrsz<=self.def_sla):
                                        res = task.apply_async(queue=self.lowq)
                                        print "Task no ",count," ",task," ",res," assigned to ",self.lowq
                                        tasktype = task.type.name[task.type.name.rfind(".")+1:]
                                        self.taskidtypedict[res] = tasktype
                                        self.isheldqtaskavailable == False
                                        flag = True
                                        self.cond.acquire()
                                        self.def_ctrsz = self.def_ctrsz + self.tasktimes[tasktype]
                                        self.cond.release()
                        elif(priority==1):
                                if (self.hp_ctrsz == 0):
                                        res = task.apply_async(queue=self.highq)
                                        print "Task no ",count," ", task," ",res," assigned to ",self.highq
                                        tasktype = task.type.name[task.type.name.rfind(".")+1:]
                                        self.taskidtypedict[res] = tasktype
                                        self.isheldqtaskavailable == False
                                        flag = True
                                        self.cond.acquire()
                                        self.hp_ctrsz = self.hp_ctrsz + self.tasktimes[tasktype]
                                        self.cond.release()
                                elif (self.def_ctrsz<=self.def_sla):
                                        res = task.apply_async(queue=self.lowq)
                                        print "Task no ",count," ",task," ",res," assigned to ",self.lowq
                                        tasktype = task.type.name[task.type.name.rfind(".")+1:]
                                        self.taskidtypedict[res] = tasktype
                                        flag= True
                                        self.isheldqtaskavailable == False
                                        self.cond.acquire()
                                        self.def_ctrsz = self.def_ctrsz + self.tasktimes[tasktype]
                                        self.cond.release()
                        print "Queue Size :: default queue size ",self.def_ctrsz,", High Priority Queue size ",self.hp_ctrsz
                        if count%5 == 0:
                            time.sleep(5)
                        count = count + 1
                        if flag == False:
                                self.isheldqtaskavailable = True
                                
def pick_random(prob_list):
  r, s = random.random(), 0
  for num in prob_list:
    s += num[1]
    if s >= r:
      return num[0]
  
        
def main():
        held_taskq = Queue.Queue()
        taskslist=[]
        count = 1
        highq = sys.argv[0]
        lowq = sys.argv[1]
        totaltasks = sys.argv[2]
        for i in range(int(totaltasks)):
                arg1 = randint(0,100) 
                arg2 = randint(0,100)                
                priority = pick_random([(0,.2),(1,.8)])
                if priority == 0:
                    count = count + 1
                    task = (add.s(arg1,arg2),1)
                else:
                    task = (add.s(arg1,arg2),1)
                taskslist.append(task)
                #held_taskq.put(task)
                #count = count + 1
        #print "total high tasks ",count  
        FILE = open("tasks5.txt", 'w')
        cPickle.dump(taskslist, FILE)
        FILE.close()
             
    
       
        FILE = open("tasks5.txt", 'r')
        taskslist = cPickle.load(FILE)
        FILE.close()
        print "Task list"
        print taskslist
        for item in taskslist:
            held_taskq.put(item)
        
        cond = Condition()
        t = my_monitor(held_taskq,highq,lowq,cond) #instance for the my_monitor class
        t.daemon = True
        t.start()
        t.test()


if __name__ == "__main__":
        main()
        