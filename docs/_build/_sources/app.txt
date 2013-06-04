Application
===========

We need Celery instance and tasks defined before we try out our schedulers. 

In this tutorial you will keep everything contained in a single module.

Creating Task
-------------

Let’s create the file tasks.py:

from celery import Celery

celery = Celery('tasks', broker='amqp://guest@localhost//',backend='')

@celery.task
def add(x, y):
    return x + y

The first argument to Celery is the name of the current module, this is needed so that names can be automatically generated, the second argument is the broker keyword argument which specifies the URL of the message broker you want to use, using RabbitMQ here, which is already the default option. Don't forget to replace the broker url and backend url to point to your installation location.

You defined a single task, called add, which returns the sum of two numbers.


