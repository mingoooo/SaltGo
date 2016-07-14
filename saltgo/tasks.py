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


if __name__ == '__main__':
    pass
