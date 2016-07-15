# coding: utf8
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from saltgo import SaltAPI, models, tasks
import logging
import json
import time
from multiprocessing import Process, Pool
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


logger = logging.getLogger('django')
# Create your views here.


@login_required(login_url="/login/")
def state(request):
    """state view"""
    return render(request, 'execute/state.html', locals())


@login_required(login_url="/login/")
def exec_state(request):
    """run state"""
    return render(request, 'execute/state.html', locals())


@login_required(login_url="/login/")
def command(request):
    """command view"""
    try:
        jobs = models.Jobs_History.objects.filter(is_sls=False).order_by('-start_time')[:10]
    except Exception as e:
        logger.error(e)
    return render(request, 'execute/command.html', locals())


@login_required(login_url="/login/")
def exec_cmd(request):
    """run command"""
    if request.method == 'POST':
        expr_from = request.POST.get('expr_from')
        tgt = request.POST.get('target')
        cmd = request.POST.get('command')
        if expr_from and tgt and cmd:
            try:
                logger.info(u'执行命令,(expr_from: %s, target: %s, command: %s)' % (expr_from, tgt, cmd))
                api = SaltAPI.SaltAPI()
                ret = api.shell_cmd(tgt, cmd, expr_from)
            except Exception as e:
                logger.error(e)
                error_msg = '执行出错！'
                return render(request, 'execute/command.html', locals())
            if ret:
                jid = ret.get('jid')
                logger.info(u'提交任务成功,jid: %s' % jid)
                minions = ret.get('minions')
                total = len(minions)
                minions_s = ','.join(minions)
                u = request.user
                user_obj = User.objects.get(username=u)
                h = models.Jobs_History(
                    jid=jid,
                    expr_from=expr_from,
                    target=minions_s,
                    command=cmd,
                    user=user_obj
                )
                h.save()
                tasks.save_result.delay(jid, total)
                return redirect('command')
            else:
                jobs = models.Jobs_History.objects.filter(is_sls=False).order_by('-start_time')[:10]
                error_msg = '没有匹配的主机！'
                logger.warning(u'没有匹配的主机！')
                return render(request, 'execute/command.html', locals())
        else:
            jobs = models.Jobs_History.objects.filter(is_sls=False).order_by('-start_time')[:10]
            error_msg = '信息不完整！'
            logger.warning(u'信息不完整！')
            return render(request, 'execute/command.html', locals())
    return redirect('command')


@login_required(login_url="/login/")
def get_result(request, jid):
    """ result view """
    try:
        ret = models.Jobs_Result.objects.get(jid=jid)
        u = models.Jobs_History.objects.get(jid=jid).user
        res = json.loads(ret.result)
    except Exception as e:
        logger.error(e)
    return render(request, 'execute/result.html', locals())


