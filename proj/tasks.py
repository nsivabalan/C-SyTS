'''
Created on Jun 4, 2013

@author: sivabalan
'''
from __future__ import absolute_import
import time
from proj.celery import celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery.task
def add(x, y):
     time.sleep(10)
     return x + y


@celery.task
def mul(x, y):
     return x * y


@celery.task
def add1(x, y):
     time.sleep(30)
     return x + y


@celery.task
def add2(x, y):
     time.sleep(60)
     return x + y


@celery.task
def mul1(x, y):
    time.sleep(3)
    return x * y
 
@celery.task
def xsum(numbers):
     return sum(numbers)

@celery.task
def infinite(x):
     for i in xrange(10000000):
          x = x + i
     return x
 
@celery.task 
def sleep1(x):
    time.sleep(1)
    return x

@celery.task
def sleep2(x):
    time.sleep(10)
    return 2*x
 
 
