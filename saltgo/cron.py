# coding: utf8

from saltgo import SaltAPI
import logging
from saltgo import models

logger = logging.getLogger('django')


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

