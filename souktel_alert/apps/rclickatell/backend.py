import urllib
import urlparse
import pprint
import datetime

from django.http import QueryDict
from django.db import DatabaseError

from rapidsms.log.mixin import LoggerMixin
from rapidsms.backends.base import BackendBase


class ClickatellBackend(BackendBase):
    '''A RapidSMS backend for Clickatell'''

    def _logger_name(self):
        return 'clickatell-backend'

    def configure(self, *args, **kwargs):
        self.debug('Registered')
    
    def send(self, message):
        self.debug('send: {0}'.format(message))


# class ClickatellHandler(RapidBaseHttpHandler, LoggerMixin):
#     '''An HttpHandler for the Clickatell mobile gateway'''  
#     
#     # This is the format of the post string
#     # http://api.clickatell.com/http/sendmsg?user=xxxxx&password=xxxxx&api_id=xxxxx&to=xxxxxxxxx&from=xxxxxxx&text=Meet+me+outside 
#     # user: clickatell username
#     # password: clickatell password
#     # api_id: unique id for account on clickatel api
#     # to: number of the sms receiver
#     # from: number of the sms sender
#     # text: short message text
#     
#     param_text = "text"
#     param_sender = "from"
#     
#     outgoing_url = "https://api.clickatell.com/http/sendmsg"
#     # api_id (customer identification number)
#     # user: clickatell username
#     # password: clickatell password
#     # to: number of the sms receiver
#     # text: short message text
#     outgoing_params = {"api_id" : "add", 
#                        "user" : "defaults", 
#                        "password" : "here",
#                      "from" : "from_number"
#                        }
#     param_text_outgoing = "text"
#     param_dst_outgoing = "to"
#     param_sender_outgoing = "from"
# 
#     @classmethod
#     def outgoing(class_, message):
#         class_.backend.info("outgoing: {0}".format(message))
