from django.http import HttpResponse
import json
from bson import json_util
import multiprocessing
import pylog485app.record
import pylog485app.send
import pylog485app.monitor
from pylog485app.models import Readings, Conf
from datetime import datetime
from django.conf import settings
import traceback
from time import time, sleep

def status(request):
    def _get_conf():
        for ob in Conf.objects.all():
            try:
                if json_util.loads(ob.meta)['label'] == settings.METEO_CONF:
                    return json_util.loads(ob.data)
            except:
                print traceback.format_exc()
                pass
        raise BaseException('could not find the configuration %s' %settings.METEO_CONF)
    try:
        cmd = request.GET.get("cmd",None)
        dic = {}
        if cmd == "conf":
            dic['conf'] = _get_conf()
        if cmd == "overview":
            dic['this process'] = multiprocessing.current_process().name
            dic['active child processes'] = [m.name for m in  multiprocessing.active_children()]
            dic['utc time'] = str(datetime.utcnow())
            dic['configuration label'] = settings.METEO_CONF

        if cmd == "recentdata":
            #dic["the last 5 recorded stamps in local DB"] = [{'data':json_util.loads(ob.data), 'meta':json_util.loads(ob.meta)} for ob in Readings.objects.all().order_by('-id')[:5]]
            dic["the last 20 recorded stamps in local DB"] = [str({'data':json_util.loads(ob.data), 'meta':json_util.loads(ob.meta)}) for ob in Readings.objects.all().order_by('-id')[:20]]
            #dic["the last 5 recorded stamps in local DB"] = [('data=' + ob.data + "    meta=" + ob.meta) for ob in Readings.objects.all().order_by('-id')[:5]]
        jdic= json_util.dumps(dic)
    except:
        err = traceback.format_exc()
        jdic = json.dumps({"error": err})

    return HttpResponse(jdic, content_type='application/json')

class MP():
    def __init__(self, name, target, request, cmd=None):
        self.t1 = time()
        self.name = name
        self.target = target
        self.request = request
        self.cmd = cmd if cmd else request.GET.get("cmd", None)
        self.dic = {}
        self.conf_label = settings.METEO_CONF


    def get_conf(self):
        for ob in Conf.objects.all():
            try:
                print json_util.loads(ob.meta)['label']
                if json_util.loads(ob.meta)['label'] == self.conf_label:
                    return json_util.loads(ob.data)[self.name]
            except:
                print traceback.format_exc()
                pass
        raise BaseException('could not find the configuration %s' %self.conf_label)

    def start(self):
        conf = self.get_conf()
        p = multiprocessing.Process(name=self.name, target=self.target, kwargs=conf)
        p.start()


    def ison(self):
        ac = [m for m in multiprocessing.active_children() if m.name == self.name ]
        if len(ac) == 0:
            return False
        else:
            return ac[0].is_alive()

    def stop(self):
        ac = [m for m in  multiprocessing.active_children() if self.name == m.name]
        if ac:
            ac[0].terminate()
            sleep(0.5)
            return True
        else:
            return False

    def process_command(self):
        lis = []
        lis.append('provided GET parameters are %s' %json_util.dumps(self.request.GET if self.request else None))
        print "%s conf = %s" %(self.name, self.conf_label)
        ison_at_start = self.ison()

        if self.cmd is None:
            lis.append('no cmd has provided')

        elif self.cmd == 'start':
            if ison_at_start:
                lis.append('process was already running')
            else:
                self.start()
                lis.append('process has been started')
        elif self.cmd == 'stop':
            if self.stop():
                lis.append('terminated process')
            else:
                lis.append('process was not running')

        elif self.cmd == 'status':
            self.dic["%s process configuration" %self.name] = self.get_conf()
        else:
            lis.append("we didnt understand your cmd")

        #respond with some info
        self.dic['log'] = lis
        self.dic['ison'] = self.ison()
        self.dic['took'] = "%s seconds" %(time()-self.t1)


def record(request):
    try:
        mp = MP(name='record', target=pylog485app.record.record, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
    return HttpResponse(dic, content_type='application/json')


def send(request):
    try:
        mp = MP(name='send', target=pylog485app.send.send, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
    return HttpResponse(dic, content_type='application/json')

def monitor(request):
    try:
        mp = MP(name='monitor', target=pylog485app.monitor.monitor, request=request)
        mp.process_command()
        dic = json.dumps(mp.dic)
    except:
        err = traceback.format_exc()
        dic = json.dumps({"error": err})
    return HttpResponse(dic, content_type='application/json')


















