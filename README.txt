Weclome to Cloud based multi-tasking Task Scheduling[C-SyTS] !

This is a task scheduling engine which assigns tasks to remote instances through various scheduling mechanisms.

Few components are required to get this system up and running. 
Celery and python is expected to be installed in local as well as all remote node. Both celery.py and tasks.py(where we create a celery instance, and where we define our tasks) should be located in all nodes.

Make sure Rabbitmq server and redis is installed in atleast one machine and make all nodes refer to the server hosting it. 

Driver is used to send tasks as input to schedulers. Driver takes in a parameter of scheduler type (FCFS/Random) based on which the corresponding Scheduler is invoked. While trying out FCFS Scheduler or Randomized Scheduler, don't forget to have mymonitor.py running in the background in order to get the total turn around time.

Queue Length Based Scheduler can be involed direclty with the script QLBS.py.

Prioritized Scheduler can be invoked with PrioritizedScheduler.py by passing in 3 parameters; first parameter is the high priority queue name, second parameter is the default priority queue name and third one is the total number of tasks to be generated.
