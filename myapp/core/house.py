# -*- coding: utf8 -*-

def run_import_houses_task(url):

  from queue.tasks import import_houses_task

  import_houses_task.delay(current_user_id(), url)


