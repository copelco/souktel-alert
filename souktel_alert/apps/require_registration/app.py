import re

from rapidsms.apps.base import AppBase
from rapidsms.models import Contact


reg_re = re.compile(r'reg [\s\w]+')


class RegApp(AppBase):

    def start(self):
        self.info('started')

    def handle(self, msg):
        if not msg.connection.contact_id:
            if reg_re.match(msg.text):
                try:
                    keyword, name = msg.text.split(' ', 1)
                except ValueError:
                    msg.respond('Plase try again')
                    return True
                try:
                    first_name, last_name = name.split(' ', 1)
                except:
                    first_name = name
                    last_name = ''
                contact = Contact.objects.create(first_name=first_name,
                                                 last_name=last_name)
                msg.connection.contact = contact
                msg.connection.save()
                msg.respond('Thank you for registering')
                return True
            body = 'You must register first. Please reply with "reg <name>"'
            msg.respond(body)
            return True
