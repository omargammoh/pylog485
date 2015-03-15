from django.conf.urls import patterns, include, url
from django.contrib import admin

import pylog485app.views as views
import pylog485app.views.pages
import pylog485app.views.data

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.pages.home, name='home'),
    url(r'^record/$', views.data.record),
    url(r'^send/$', views.data.send),
    url(r'^status/$', views.data.status),
    url(r'^monitor/$', views.data.monitor),
    url(r'^admin/', include(admin.site.urls)),
)
