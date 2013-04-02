from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # AUTHENTICATION VIEWS
    url(r'^login/$', auth_views.login, {'template_name': 'auth/login.html',},
        name='login_view'),
    url(r'^logout/$', auth_views.logout_then_login,
        name='logout_then_login_view'),
    url(r'^password_change/$', auth_views.password_change,
        {'template_name': 'auth/password.html',}, name='password_view'),
    url(r'password_change_done/$', auth_views.password_change_done,
        {'template_name': 'auth/password_change_done.html',},
        name='password_done_view'),
        
    url(r'^cuff/', include('cuff.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

try:
    from local_urls import *
except:
    pass
