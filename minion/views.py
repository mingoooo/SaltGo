from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from saltgo import models
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


logger = logging.getLogger('django')
# Create your views here.


@login_required(login_url='/login')
def minion_status(request):
    try:
        model_obj = models.Minion_Status.objects.all()
        contacts = _make_paginator(request, model_obj)
    except Exception as e:
        logger.error(e)
    return render(request, 'minion/minion_status.html', locals())


def _make_paginator(request, model_obj):
    one_page_show = request.GET.get('one_page_show')
    if not one_page_show:
        one_page_show = 20
    page = request.GET.get('page')
    if not page:
        page = 1
    paginator = Paginator(model_obj, one_page_show)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    return contacts


@login_required(login_url='/login')
def key_status(request):
    pass


@login_required(login_url='/login')
def key_manage(request):
    pass
