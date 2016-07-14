from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required(login_url='/login')
def minion_status(request):
    return render(request, 'minion/minion_status.html', locals())
