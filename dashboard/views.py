from django.shortcuts import render
from saltgo import models
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required(login_url="/login/")
def index(request):
    return render(request, 'dashboard/index.html', locals())
