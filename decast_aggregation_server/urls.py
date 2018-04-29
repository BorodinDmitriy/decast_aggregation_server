"""decast_aggregation_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns
from server import views

devices_urls = [
    url(r'^$', views.DeviceList.as_view()),
    url(r'^(?P<id>[0-9]+)/$', views.DeviceDetail.as_view()),
    url(r'^(?P<id>[0-9]+)/readings/$', views.DeviceReadings.as_view()),
    
    url(r'^(?P<id>[0-9]+)/get_pay_bill/', views.GetPayBill.as_view()),
    url(r'^(?P<id>[0-9]+)/change_device_account/', views.ChangeDeviceAccount.as_view()),
  ]

user_urls = [
    url(r'^$', views.UserByEmail.as_view()),
  ]

users_urls = [
    url(r'^(?P<id>[0-9]+)/devices/$', views.DevicesByUserId.as_view()),
  ]

eirc_urls = [
    url(r'^$', views.EIRCDeviceList.as_view()),
    url(r'^(?P<id>[0-9]+)/$', views.EIRCDeviceDetail.as_view()),
  ]

rates_urls = [
    url(r'^$', views.RateList.as_view()),
    url(r'^(?P<id>[0-9]+)/$', views.RateDetail.as_view()),
  ]
rate_urls = [
    url(r'^$', views.RateByType.as_view()),
  ]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^devices/',include(devices_urls)),
    url(r'^user/',include(user_urls)),
    url(r'^users/',include(users_urls)),
    url(r'^eirc_devices/',include(eirc_urls)),
    url(r'^rate/',include(rate_urls)),
    url(r'^rates/',include(rates_urls)),

    url(r'^auth/send_report/$',views.SendAuthRep.as_view()),
    url(r'^worker/$',views.SendWorker.as_view()),
    #url(r'^user/$', devices_views.UserByEmail.as_view()),
    #url(r'^devices/$', devices_views.DeviceList.as_view()),
   # url(r'^devices/(?P<id>[0-9]+)/$', devices_views.DeviceDetail.as_view()),
   # url(r'^users/(?P<id>[0-9]+)/devices/$', devices_views.DevicesByUserId.as_view()),
   # url(r'^devices/(?P<id>[0-9]+)/readings$', devices_views.DeviceReadings.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
