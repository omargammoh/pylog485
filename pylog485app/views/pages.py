from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json
import multiprocessing




def home(request, template_name='home.html'):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))

def xhome(request):
    dic = {'where am i':"you are home"}
    dic['active_cildren'] = [m.name for m in  multiprocessing.active_children()]
    dic['current process'] = multiprocessing.current_process().name
    return HttpResponse(json.dumps(dic), content_type='application/json')

