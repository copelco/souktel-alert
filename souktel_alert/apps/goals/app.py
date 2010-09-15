import datetime

from rapidsms.apps.base import AppBase
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule


SCHEDULE_DESC = 'goals-cron-job'
CALLBACK = 'goals.app.scheduler_callback'


def scheduler_callback(router):
    """
    Basic rapidsms.contrib.scheduler.models.EventSchedule callback
    function that runs GoalsApp.status_update()
    """
    app = router.get_app("goals")
    app.status_update()


class GoalsApp(AppBase):
    """ RapidSMS app to track goal setting """

    cron_schedule = {'minutes': '*'}
    notification_treshold = datetime.timedelta(minutes=30)
    template = 'In %(month)s., you stated that your goal was "%(goal)s". '\
               'How are you progressing towards this goal? Text "goal" '\
               'with a number from 0 to 5, where 5 = great progress, 0 '\
               '= no progress, e.g. "goal 4"'

    def start(self):
        data = {
            'callback': CALLBACK,
            'description': SCHEDULE_DESC,
        }
        data.update(self.cron_schedule)
        schedule, created = EventSchedule.objects.get_or_create(**data)
        if created:
            self.debug('{0} created'.format(SCHEDULE_DESC))
        else:
            self.debug('{0} exists'.format(SCHEDULE_DESC))
        self.info('started')

    def status_update(self):
        """ Cron job that's executed every minute """
        from goals.models import Goal

        self.debug('{0} running'.format(SCHEDULE_DESC))
        start_date = datetime.datetime.now() - self.notification_treshold
        goals = Goal.objects.filter(date_last_notified__lt=start_date,
                                    in_session=True)
        for goal in goals:
            msg = OutgoingMessage(connection=goal.connection,
                                  template=self.template,
                                  goal=goal.body)
            msg.send()
            goal.date_last_notified = datetime.datetime.now()
            goal.save()
