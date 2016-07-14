# coding: utf8

from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
import logging


logger = logging.getLogger('django')
# Create your views here.


def login(request):
    error_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                logger.info(u'用户登陆: %s' % username)
                _next = request.POST.get('next')
                if not _next:
                    _next = '/'
                print request.session.items()
                return HttpResponseRedirect(_next)
            else:
                logger.warning(u'账户禁用,登陆用户名: %s' % username)
                error_msg = '账户已禁用'
        else:
            logger.warning(u'用户名或密码错误,登陆用户名: %s' % username)
            error_msg = '用户名或密码错误'
    return render(request, 'account/login.html', locals())


def logout(request):
    auth_logout(request)
    return redirect('login')
