FCFS Scheduler
==============

FCFS Scheduler is readily available from C-SyTS. FCFS assigns tasks in the order they arrive. Tasks are assigned in a round robin fashion to the available worker nodes.

Driver module should be used to send tasks to our C-SyTS. It takes as input the type of scheduler to be used for task execution. Tasks are generated on the fly within driver module. You can modify it to generate your own tasks if required.

Command to invoke FCFS Scheduler:
---------------------------------

python Driver.py FCFS


If you wish to monitor the task success event, run mymonitor.py as a separate thread.

Please make sure to modify broker url and backend url in your celery instance. Also the available worker nodes are hard-coded as of now in Driver.py module. Also, ensure that the task being invoked is actually defined in the application being used and is available in all remote worker nodes being used during task execution.



