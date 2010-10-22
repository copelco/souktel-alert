from rapidsms.apps.base import AppBase


class CatchAllApp(AppBase):
    def default(self, msg):
        if hasattr(msg, 'logger_msg'):
            msg.logger_msg.free_text = True
            msg.logger_msg.save()
            return True
