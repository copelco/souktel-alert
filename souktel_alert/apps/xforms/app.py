import rapidsms

from rapidsms.apps.base import AppBase
from .models import XForm

class App (AppBase):


    def handle (self, message):
        # pull out the first word (keyword)
        keyword = message.text.split()[0].lower()

        # see if this message matches any of our forms
        for form in XForm.objects.all().filter(active=True):
            if form.keyword == keyword:
                submission = form.process_sms_submission(message.text, message.connection)

                if submission.errors:
                    message.respond("Error:  %s" %  submission.errors[0])
                else:
                    message.respond(form.response)
                return True

        return False
        
