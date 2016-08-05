# coding: utf8
from django.shortcuts import render, redirect
from saltgo import SaltAPI, models, tasks
import logging
import json
import os.path
import posixpath
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, ContentType
from django.conf import settings
from django.views.decorators.csrf import csrf_protect


logger = logging.getLogger('django')
# Create your views here.


@login_required(login_url="/login/")
def state(request):
    """state view"""
    try:
        jobs = models.Jobs_History.objects.filter(is_sls=True).order_by('-start_time')[:10]
        state_files = models.State_File.objects.all()
        minions = models.Minion_Status.objects.only("minion_id")
    except Exception as e:
        logger.error(e)
    return render(request, 'execute/state.html', locals())


@login_required(login_url="/login/")
def exec_state(request):
    """run state"""
    u = request.user
    u_obj = User.objects.get(username=u)
    if u_obj.has_perm('saltgo.can_execute_state'):
        if request.method == 'POST':
            expr_form = request.POST.get('expr_form')
            sls = request.POST.get('sls')
            if expr_form == 'list':
                tgt_list = request.POST.getlist('target')
                tgt = ','.join(tgt_list)
            else:
                tgt = request.POST.get('target')
            if expr_form and tgt and sls:
                if sls == 'highstate':
                    if u_obj.has_perm('saltgo.can_execute_highstate'):
                        logger.info(u'执行highstate,(expr_form: %s, target: %s)' % (expr_form, tgt))
                        sapi = SaltAPI.SaltAPI()
                        ret = sapi.execute_highstate(tgt, expr_form)
                    else:
                        logger.warning(u'用户缺少权限执行highstate: %s' % u)
                        error_msg = '权限不足！'
                        jobs = models.Jobs_History.objects.filter(is_sls=True).order_by('-start_time')[:10]
                        state_files = models.State_File.objects.all()
                        minions = models.Minion_Status.objects.only("minion_id")
                        return render(request, 'execute/state.html', locals())
                else:
                    if u_obj.has_perm('saltgo.can_execute_' + sls):
                        logger.info(u'执行state文件,(expr_form: %s, target: %s, sls: %s)' % (expr_form, tgt, sls))
                        sls_obj = models.State_File.objects.get(state_code=sls)
                        sls_path = sls_obj.state_file_path
                        sapi = SaltAPI.SaltAPI()
                        ret = sapi.execute_state(tgt, sls_path, expr_form)
                    else:
                        logger.warning(u'用户缺少权限执行%s: %s' % (sls, u))
                        error_msg = '权限不足！'
                        jobs = models.Jobs_History.objects.filter(is_sls=True).order_by('-start_time')[:10]
                        state_files = models.State_File.objects.all()
                        minions = models.Minion_Status.objects.only("minion_id")
                        return render(request, 'execute/state.html', locals())
                if ret:
                    jid = ret.get('jid')
                    logger.info(u'提交任务成功,jid: %s' % jid)
                    minions = ret.get('minions')
                    total = len(minions)
                    minions_s = ','.join(minions)
                    h = models.Jobs_History(
                        jid=jid,
                        expr_form=expr_form,
                        target=minions_s,
                        sls=sls,
                        user=u_obj,
                        is_sls=True
                    )
                    h.save()
                    tasks.save_result.delay(jid, total)
                else:
                    error_msg = '没有匹配的主机！'
                    logger.warning(u'没有匹配的主机！')
                    jobs = models.Jobs_History.objects.filter(is_sls=True).order_by('-start_time')[:10]
                    state_files = models.State_File.objects.all()
                    minions = models.Minion_Status.objects.only("minion_id")
                    return render(request, 'execute/state.html', locals())
            else:
                logger.warning(u'信息不完整！')
                error_msg = '信息不完整！'
                jobs = models.Jobs_History.objects.filter(is_sls=True).order_by('-start_time')[:10]
                minions = models.Minion_Status.objects.only("minion_id")
                return render(request, 'execute/state.html', locals())
    else:
        logger.warning(u'用户缺少权限执行state file: %s' % u)
        error_msg = '权限不足！'
        jobs = models.Jobs_History.objects.filter(is_sls=True).order_by('-start_time')[:10]
        state_files = models.State_File.objects.all()
        minions = models.Minion_Status.objects.only("minion_id")
        return render(request, 'execute/state.html', locals())
    return redirect('state')


@login_required(login_url="/login/")
def command(request):
    """command view"""
    try:
        jobs = models.Jobs_History.objects.filter(is_sls=False).order_by('-start_time')[:10]
        minions = models.Minion_Status.objects.only("minion_id")
    except Exception as e:
        logger.error(e)
    return render(request, 'execute/command.html', locals())


@login_required(login_url="/login/")
def exec_cmd(request):
    """run command"""
    if request.method == 'POST':
        expr_form = request.POST.get('expr_form')
        cmd = request.POST.get('command')
        if expr_form == 'list':
            tgt_list = request.POST.getlist('target')
            tgt = ','.join(tgt_list)
        else:
            tgt = request.POST.get('target')
        if expr_form and tgt and cmd:
            try:
                logger.info(u'执行命令,(expr_form: %s, target: %s, command: %s)' % (expr_form, tgt, cmd))
                api = SaltAPI.SaltAPI()
                ret = api.shell_cmd(tgt, cmd, expr_form)
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
                    expr_form=expr_form,
                    target=minions_s,
                    command=cmd,
                    user=user_obj
                )
                h.save()
                tasks.save_result.delay(jid, total)
            else:
                jobs = models.Jobs_History.objects.filter(is_sls=False).order_by('-start_time')[:10]
                minions = models.Minion_Status.objects.only("minion_id")
                error_msg = '没有匹配的主机！'
                logger.warning(u'没有匹配的主机！')
                return render(request, 'execute/command.html', locals())
        else:
            jobs = models.Jobs_History.objects.filter(is_sls=False).order_by('-start_time')[:10]
            minions = models.Minion_Status.objects.only("minion_id")
            error_msg = '信息不完整！'
            logger.warning(u'信息不完整！')
            return render(request, 'execute/command.html', locals())
    return redirect('command')


@login_required(login_url="/login/")
def result(request, jid):
    """ result view """
    try:
        logger.info(u'获取result数据: %s' % jid)
        ret = models.Jobs_Result.objects.get(jid=jid)
        u = models.Jobs_History.objects.get(jid=jid).user
        res = json.loads(ret.result)
        for k, v in res.items():
            if not isinstance(v, str):
                res[k] = json.dumps(v, sort_keys=True, indent=4, separators=(',', ': '))
    except Exception as e:
        logger.error(e)
    return render(request, 'execute/result.html', locals())


@login_required(login_url="/login/")
def flush_state_file(request):
    if request.method == 'POST':
        u = request.user
        u_obj = User.objects.get(username=u)
        logger.info(u'用户刷新state文件: %s' % u)
        if u_obj.has_perm('saltgo.can_execute_state'):
            master_id = settings.SALT_MASTER_MINION_ID
            state_dir = settings.SALT_MASTER_STATE_DIR
            api = SaltAPI.SaltAPI()
            state_list = [i for i in api.file_find_sync(master_id, state_dir).get(master_id) if i.endswith('.sls')]
            logger.info(u'获取state文件列表: %s' % state_list)
            for i in state_list:
                state_code = i.split('/')[-1].split('.')[0]
                state_file_path = posixpath.relpath(i, settings.SALT_MASTER_BASE).split('sls')[0].rstrip('.').replace('/', '.')
                try:
                    state_obj = models.State_File.objects.get(state_code=state_code)
                except models.State_File.DoesNotExist:
                    perm_name = 'Can execute %s' % state_code
                    logger.info(u'添加执行state权限: %s' % perm_name)
                    content_obj = ContentType.objects.get(model='state_file')
                    perm_obj = models.Permission(
                        name=perm_name,
                        content_type=content_obj,
                        codename='can_execute_' + state_code
                    )
                    perm_obj.save()
                    logger.info(u'添加state文件: %s' % i)
                    state_obj = models.State_File(
                        state_name=state_code,
                        state_code=state_code,
                        is_valid=True,
                        author=u_obj,
                        permission=perm_obj,
                        state_file_path=state_file_path
                    )
                    state_obj.save()
        else:
            logger.warning(u'用户缺少权限刷新state file: %s' % u)
            error_msg = '权限不足！'
            jobs = models.Jobs_History.objects.filter(is_sls=True).order_by('-start_time')[:10]
            state_files = models.State_File.objects.all()
            minions = models.Minion_Status.objects.only("minion_id")
            return render(request, 'execute/state.html', locals())
    return redirect('state')
