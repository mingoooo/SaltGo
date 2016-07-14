"""saltgo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.command, name='command'),
    url(r'^command/$', views.command, name='command'),
    url(r'^exec_cmd/$', views.exec_cmd, name='exec_cmd'),
    url(r'^state/$', views.state, name='state'),
    url(r'^exec_state/$', views.exec_state, name='exec_state'),
    url(r'^result/(?P<jid>[0-9]+)$', views.get_result, name='get_result'),
]
