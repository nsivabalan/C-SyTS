'''
Created on Jun 4, 2013

@author: sivabalan
'''

from __future__ import absolute_import

from celery import Celery

celery = Celery('proj.celery',
               broker='amqp://guest:guest@128.111.55.219',
                backend='redis://128.111.55.219',
                include=['proj.tasks'])


# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_RESULT_BACKEND='redis://128.111.55.219',
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_SEND_TASK_SENT_EVENT = True,
)

if __name__ == '__main__':
    celery.start()

