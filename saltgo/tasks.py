# coding: utf8

import time
import logging
from celery import task
from saltgo import models, SaltAPI
import json

logger = logging.getLogger('django')


@task()
def save_result(jid, total):
    """ save result to db """
    ret = {}
    count = 0
    sapi = SaltAPI.SaltAPI()
    while not ret or count > 20:
        ret = sapi.jobs_lookup(jid)
        count += 1
        time.sleep(3)
    if ret:
        succeed = len(ret)
        failed = total - succeed
        r = models.Jobs_Result(jid_id=jid, succeed=succeed, failed=failed, result=json.dumps(ret))
        r.save()
    else:
        succeed = 0
        failed = total
        r = models.Jobs_Result(jid_id=jid, succeed=succeed, failed=failed, result=u"获取返回结果失败, jid: %s" % jid)
        r.save()
        logger.error(u"获取返回结果失败, jid: %s" % jid)


@task()
def update_minion_status():
    """ get minion status and update db """
    try:
        api = SaltAPI.SaltAPI()
        online_status_dict = api.runner_sync('manage.status')
        up_list = online_status_dict.get('up')
        down_list = online_status_dict.get('down')
        key_status_dict = api.wheel_key_list().get('data').get('return')
        r_key_list = key_status_dict.get('minions_rejected')
        d_key_list = key_status_dict.get('minions_denied')
        u_key_list = key_status_dict.get('minions_pre')
        a_key_list = key_status_dict.get('minions')
    except Exception as e:
        logger.error(u'获取minion状态失败, error code: %s' % e)
        exit(1)
    else:
        for minion in up_list:
            ks = 'NULL'
            if minion in r_key_list:
                ks = 'R'
            elif minion in d_key_list:
                ks = 'D'
            elif minion in u_key_list:
                ks = 'U'
            elif minion in a_key_list:
                ks = 'A'
            obj, created = models.Minion_Status.objects.update_or_create(
                minion_id=minion,
                defaults={'is_online': True, 'key_status': ks}
            )
            if created:
                logger.info(u'插入新minion: %s' % minion)
            obj.save()
        for minion in down_list:
            ks = 'NULL'
            if minion in r_key_list:
                ks = 'R'
            elif minion in d_key_list:
                ks = 'D'
            elif minion in u_key_list:
                ks = 'U'
            elif minion in a_key_list:
                ks = 'A'
            obj, created = models.Minion_Status.objects.update_or_create(
                minion_id=minion,
                defaults={'is_online': False, 'key_status': ks}
            )
            if created:
                logger.info(u'插入新minion: %s' % minion)
            obj.save()


if __name__ == '__main__':
    pass
