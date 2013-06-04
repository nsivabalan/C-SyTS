'''
Created on Jun 4, 2013

@author: sivabalan
'''
from celery.events import EventReceiver
from kombu import Connection as BrokerConnection
import sys,datetime
import redis

def my_monitor(app):
    state = app.events.State()
    my_monitor.r_server =  redis.Redis("128.111.55.219")
    my_monitor.count = 0
        
    def announce_failed_tasks(event):
        state.event(event)
        task_id = event['uuid']

        print('TASK FAILED: %s[%s] ' % (
            event['hostname'], task_id, ))
        
    def announce_succeeded_tasks(event):
        print "Event received"
        state.event(event)
        task_id = event['uuid']
        runtime = event['runtime']
        hostname = event['hostname']
        timestamp = event['timestamp']
        result = event['result']

        print('TASK SUCCEEDED: %s - %s with execution time of %s having result %s and timestamp %s' % (
            hostname, task_id, runtime,result,timestamp,))
        pipe = my_monitor.r_server.pipeline()
        pipe.hset("celery-taskSucceeded:"+task_id,"result",result)
        pipe.hset("celery-taskSucceeded:"+task_id,"runtime",runtime)
        pipe.hset("celery-taskSucceeded:"+task_id,"hostname",hostname)
        pipe.hset("celery-taskSucceeded:"+task_id,"timestamp",timestamp)
        pipe.sadd("tasklist",task_id)
        pipe.execute()
        
        
        my_monitor.count = my_monitor.count +1
        b = datetime.datetime.now()
        c = b - my_monitor.a
        print c
        print divmod(c.days * 86400 + c.seconds, 60)," for ",my_monitor.count," tasks"
        

    while True:
        my_monitor.a = datetime.datetime.now()
        try:
            
                with app.connection() as connection:
                    recv = app.events.Receiver(connection, handlers={
                           # 'task-started': on_event,                                         
                            'task-succeeded': announce_succeeded_tasks,
                            #'task-failed': announce_failed_tasks,
                    })
                    recv.capture(limit=None, timeout=None, wakeup=True)
        except (KeyboardInterrupt, SystemExit):
            print "EXCEPTION KEYBOARD INTERRUPT"
            sys.exit()
        
if __name__ == '__main__':
    from proj.celery import celery
    my_monitor(celery)