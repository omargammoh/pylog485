"""
WSGI config for pylog485 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")


#>>>>OGA
import pylog485app.views.data
import multiprocessing
print '-'*20
print 'initializing processes'
ac = [m.name for m in multiprocessing.active_children()]
print 'processes before: %s' %ac
try:
    if not ("record" in ac):
        print 'initoalizing record'
        p_rec = pylog485app.views.data.MP(name='record', target=pylog485app.record.record, request=None, cmd="start")
        p_rec.process_command()
    if not ("send" in ac):
        print 'initializing send'
        p_rec = pylog485app.views.data.MP(name='send', target=pylog485app.send.send, request=None, cmd="start")
        p_rec.process_command()
except:
    "!!unable to initialize the processes"
ac = [m.name for m in multiprocessing.active_children()]
print 'processes after: %s' %ac
print '-'*20
#<<<<<



from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
