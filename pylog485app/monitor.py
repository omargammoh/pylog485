import numpy as np
import os, django
from datetime import datetime, timedelta
from time import sleep, time
import traceback
from bson import json_util

def _Vs(Vth, t, RC, Rratio):
    ret = Vth / (1 + (Rratio - 1.) * np.exp( -1. * t / RC))
    return ret

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    print "!!!no RPI.GPIO module"

def _RCtime(gpio_pin, Vth, RC, Rratio, sl = 0.001, timeout = 10):
    """
    a function that sets the GPIO pin low, then measures how long it would take for the pin to be high
    sl: the measurement resolution in seconds
    """

    # Discharge capacitor
    GPIO.setup(gpio_pin, GPIO.OUT)
    GPIO.output(gpio_pin, GPIO.LOW)
    sleep(2.)
    # Count loops until voltage across
    # capacitor reads high on GPIO
    i = 0
    GPIO.setup(gpio_pin, GPIO.IN)
    t0 = time()
    while (GPIO.input(gpio_pin) == GPIO.LOW):
        if (time() - t0) > timeout:
            raise BaseException("timeout")
        sleep(sl)
        i += 1
        if i%1000 == 0:
            print "+1000"
    t1 = time()
    time_to_charge = t1 - t0

    readingtimeratio = (time_to_charge - (sl * i))/time_to_charge
    resolutionerror = 1./i

    voltage = _Vs(Vth=Vth, t=time_to_charge, RC=RC, Rratio=Rratio)
    print "    reading = %s, time_to_charge = %s" %(voltage, time_to_charge)
    print "    i = %s, readingtimeratio = %s%%, resolutionerror= %s%%" %(i,readingtimeratio*100, resolutionerror*100)
    return voltage

def _prepare_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
    django.setup()

def _decide_start(data_period, dt):
    safety = timedelta(seconds = 5)
    noms = datetime(*list((dt + safety).timetuple())[:6])#add safety margin, remove milliseconds
    today = datetime(*list(dt.timetuple())[:3])

    totalsec = (noms - today).total_seconds()

    def ceil(x,base):
        return np.ceil(x/base) * base

    if (data_period<60) and (60%data_period == 0):
        print "_decide_start: periodic seconds"
    elif (data_period<3600) and (3600%data_period == 0):
        print "_decide_start: periodic minutes"
    elif (data_period<=86400) and (86400%data_period == 0):
        print "_decide_start: periodic hours"
    else:
        raise BaseException('this stamp period cannot be periodic over minutes, hours or days %s' %data_period)

    shift = ceil(totalsec, data_period)
    starton = today + timedelta(seconds=shift)
    print "_decide_start: %s %s %s, totalsec = %s, shift = %s" %(dt, data_period, starton, totalsec, shift)
    return starton

def _get_stamp(data_period, gpio_conf):
    dic = {}
    #TODO: handle the fact that some sensors might fail while others not
    for label,conf in gpio_conf.iteritems():
        try:
            if conf['active']:
                #read
                value = _RCtime(gpio_pin=conf['gpio_pin'], Vth=conf['Vth'], RC=conf['RC'], Rratio=conf['Rratio'])
                dic[label] = value
            else:
                pass
        except:
            print '!!_RCtime: gpio reading %s failed' %label
            pass

    return dic #{'BatVolt':21.0}


def monitor(data_period, gpio_conf):
    _prepare_django()
    import pylog485app.models

    now = datetime.utcnow()
    starton = _decide_start(data_period, now)

    i = 0
    print "monitor: starton %s" %starton
    while (True):
        print '\n>>>> monitor loop, i= %s' %(i)
        #calculate the time for stamp and waiting period, and skip if this stamp is already passed
        stamp = starton + timedelta(seconds = i * data_period)#beginning ts
        wait = (stamp - datetime.utcnow()).total_seconds()
        if wait >= 0 :
            print '    wait %s sec before reading gpio data' %wait
            sleep(wait)
        else:
            skipi = int(abs(wait)/data_period) + 1
            i += skipi
            print '    !! monitor stamp missed by %s seconds, stamp = %s' %(wait, stamp)
            print '    skipping i by %s' %(skipi)
            continue

        #get the data of the stamp
        try:
            #raise exception if there is no data at all, if there is just one sensor not working, dont fail
            print '    getting samples now...'
            dic_readings = _get_stamp(data_period, gpio_conf)
            print '    [%s] now = %s' %(stamp, datetime.utcnow())
            print '    %s' %(dic_readings)

        except:
            dic_readings = None
            print traceback.format_exc()

        #add one to 1
        i += 1

        #if there is data, save it in the local db
        if dic_readings:
            try:
                dic_readings['timestamp']=stamp
                pylog485app.models.Monitor(data=json_util.dumps(dic_readings)
                        ,meta=json_util.dumps({'sent':'false', 'quality':'?'})).save()
                print "    data saved in db"

            except:
                print '    !!could not send data to local DB'
                print traceback.format_exc()
        else:
            print "    no data saved in db"

        print '<<<< m'
    return None



def _fit_and_plot(tv, extra=False):
    """
    tc is a list of time and voltage tuples
    """
    from scipy.optimize import minimize
    import numpy as np
    import matplotlib.pyplot as plt
    def error(lis):
        Vth = lis[0]
        RC = lis[1]
        lis_err = []
        for (t,v_act) in tv:
            v_calc = _Vs(Vth=Vth, t=t, RC=RC)
            err = v_calc - v_act
            lis_err.append(err)

        ret = np.mean(map(abs,lis_err))
        return ret

    x0 = [2., 4.]

    res = minimize(error, x0)


    def plot():
        trange = np.linspace(np.min(map(lambda x:x[0],tv))/4, np.max(map(lambda x:x[0],tv))*1.5, 100)
        plt.scatter(*zip(*tv))
        plt.plot(trange, map(lambda t:_Vs(Vth=res.x[0], t=t, RC=res.x[1]), trange), label= 'n=%s, Vth = %s, RC = %s' %(len(tv), res.x[0], res.x[1]))
        if extra :
            for r in np.linspace(0.5,3,10):
                plt.plot(trange, map(lambda t:_Vs(Vth=res.x[0], t=t, RC=res.x[1]*r), trange),color=(0.9, 0.9, 0.9), label= 'RC = %s' %(res.x[1] * r))
        #plt.show()

    plot()
    print 'fitted: Vth = %s, RC = %s' %(res.x[0], res.x[1])
    return res.x


if __name__ == '__main__':
    tv = [
         (0.418,11.99)
        ,(0.425017,11.9)
        ,(0.4255,11.89)
        ,(0.51633,10.07)
        ,(0.6103,8.68)
        ,(1.05774,5.45)
        ,(0.6954,7.85)
        ,(0.60716,8.76)
        ,(0.997,5.72)
        ,(1.34028,4.45)
        ,(1.52707,4.05)
        ,(0.49806,10.4)
        ,(0.87058,6.43)
        ]
    _fit_and_plot(tv,True)
    _fit_and_plot([(0.418,11.99),(0.60716,8.76),(0.997,5.72),(0.87058,6.43),(1.52707,4.05)])
    _fit_and_plot([(0.418,11.99),(1.52707,4.05)])
    plt.legend()
    plt.show()
