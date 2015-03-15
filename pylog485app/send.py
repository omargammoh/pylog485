import pymongo
import traceback

from datetime import datetime
from time import sleep, time

from django.conf import settings

import os, django
from bson import json_util

def _prepare_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
    django.setup()


def send(send_period, keep_period, mongo_address):
    '''
    send_period: every how often should i send?
    keep_period: how long should i wait before i delete the sent items
    take data from db and send it to mongodb, if successfull, mark data as successfull and delete after a while
    '''
    _prepare_django()
    import pylog485app.models

    connected = False
    sleep(10)
    i = 0
    while (True):
        print '-'*30
        print "\n>>>> send loop, i=%s" %i
        #waiting to have a connection
        t1 = time()
        j = 0
        while (not connected) :
            try :
                client = pymongo.MongoClient(mongo_address)
                db = client.get_default_database()
            except:
                pass

            connected = client.alive()
            if not connected:
                #keep trying
                retryin = min(20 * (j + 1), 60*60)
                print "    !!couldnt connect at j=%s, retrying in %s" % (j,retryin)
                sleep(retryin)
            j += 1
        t2 = time()
        print '    connected to mongo, took %s sec, and %s trials to connect' %(round(t2 - t1, 3), j)

        #when connection is good then processdata
        cnt = {'del': 0, 'send': 0}
        if connected:
            print '    processing data...'
            for ob in pylog485app.models.Readings.objects.all():
                meta = json_util.loads(ob.meta)

                #handle the unsent data
                try:
                    if meta['sent'] == 'false':
                        #send it
                        col = db['meteo_' + settings.METEO_CONF]
                        jdata=json_util.loads(ob.data)
                        col.insert(jdata)
                        #mark it as sent
                        meta['sent'] = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                        ob.meta = json_util.dumps(meta)
                        ob.save()
                        cnt['send'] += 1
                except:
                    print '    !!sending data to mongodb failed'
                    print traceback.format_exc()

                #handle the sent data
                meta = json_util.loads(ob.meta)
                if len(meta['sent']) == 4+2+2+2+2+2 and meta['sent'].isdigit():
                    sentdate = datetime.strptime(meta['sent'], "%Y%m%d%H%M%S")
                    now = datetime.utcnow()
                    #if this data point has been there for a short time, keep it
                    if (now - sentdate).total_seconds() < keep_period:
                        pass
                    #if this data point has been there for a long time, delete it
                    else:
                        ob.delete()
                        cnt['del'] += 1
        t3 = time()
        print '    updated dbs, took %s sec to process db with %s' %(round(t3 - t2,3), cnt)

        i += 1
        #waiting for next sending time
        print "    next iteration is after %s sec" %send_period
        print '<<<< s'
        sleep(send_period)

    return None
