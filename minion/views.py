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
    except Exception as e:
        logger.error(e)
    return render(request, 'minion/minion_status.html', locals())


@login_required(login_url='/login')
def key_status(request):
    pass


@login_required(login_url='/login')
def key_manage(request):
    pass
