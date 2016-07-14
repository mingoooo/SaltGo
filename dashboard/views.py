from django.shortcuts import render
from saltgo import models
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required(login_url="/login/")
def index(request):
    online_dev = models.Minion_Status.objects.filter(is_online=True).count()
    offline_dev = models.Minion_Status.objects.filter(is_online=False).count()
    return render(request, 'dashboard/index.html', locals())
