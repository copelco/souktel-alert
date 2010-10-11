import re

from rapidsms.apps.base import AppBase
from rapidsms.models import Contact, Connection


reg_re = re.compile(r'reg [\s\w]+')


class RegApp(AppBase):

    def start(self):
        self.info('started')

    def handle(self, msg):
        if not msg.connection.contact_id:
            # first search for another connection with same identity
            identity = msg.connection.identity
            try:
                conn = Connection.objects.filter(identity=identity)
                conn = conn.exclude(contact__isnull=True)[0]
            except IndexError:
                conn = None
            if conn:
                # the same number was found on a seperate backend, so
                # associate the contact and pass the message along
                msg.connection.contact = conn.contact
                msg.connection.save()
                return False
            # if no existing connection is found, see if user is registering
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
