from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler


class DapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dapi'

    def ready(self):
        from .periodic_tasks import check_ready_and_send_email

        sched = BackgroundScheduler()
        sched.add_job(check_ready_and_send_email, 'interval', seconds=1)
        sched.start()




