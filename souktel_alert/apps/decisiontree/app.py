#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.apps.base import AppBase
from rapidsms.models import Connection
from rapidsms.messages import OutgoingMessage
from models import *

from django.utils.translation import ugettext as _

#from afghansms_extensions.models import Report

class App(AppBase):
    
    registered_functions = {}
    session_listeners = {}
    
    def start(self):
        pass
    
    def configure(self, last_message="You are done with this survey.  Thanks for participating!", **kwargs):
        self.last_message = last_message
    
    def handle(self, msg):
        # if this caller doesn't have a session attribute,
        # they're not currently answering a question tree, so
        # just search for triggers and return
        sessions = Session.objects.all().filter(state__isnull=False)\
            .filter(connection=msg.connection)

        if not sessions:
            self.debug("No session found")
            try:
                tree = Tree.objects.get(trigger=msg.text)
                # start a new session for this person and save it
                self.start_tree(tree, msg.connection, msg)
                return True
            # no trigger found? 
            # put them on a default tree - changed by Mike
            except Tree.DoesNotExist:
                # This is a hack - the text will only encode in ascii if it doesn't have pashto chars
                try:
                  msg.text.encode('ascii')
                  tree, _ = Tree.objects.get_or_create(trigger="default-en")
                  self.debug("No trigger found using default-en")
                except UnicodeEncodeError:
                  tree, _ = Tree.objects.get_or_create(trigger="default-pus")
                  self.debug("No trigger found using default-pus")

                # start a new session for this person and save it
                self.start_tree(tree, msg.connection, msg)
                return True
        
        # the caller is part-way though a question
        # tree, so check their answer and respond
        else:
            session = sessions[0]
            state = session.state

            self.debug(state)
            # loop through all transitions starting with  
            # this state and try each one depending on the type
            # this will be a greedy algorithm and NOT safe if 
            # multiple transitions can match the same answer

            if msg.text == "reset":
              self._end_session(session)
              return True

            transitions = Transition.objects.filter(current_state=state)
            found_transition = None
            for transition in transitions:
                if self.matches(transition.answer, msg):
                    found_transition = transition
                    break
            
            # the number of tries they have to get out of this state
            # if empty there is no limit.  When the num_retries is hit
            # a user's session will be terminated.
    
            # not a valid answer, so remind
            # the user of the valid options.
            if not found_transition:
                transitions = Transition.objects.filter(current_state=state)
                # there are no defined answers.  therefore there are no more questions to ask 
                if len(transitions) == 0:
                    official_name = Report.objects.get(session=session).official_name
                    location = Report.objects.get(session=session).location
                    count = Report.objects.filter(official_name=official_name, location=location).count()
                    msg.respond(_("Thank you for reporting this incident. You and %s other people have reported on %s in %s.") % (count,official_name,location))
                    # end the connection so the caller can start a new session
                    self._end_session(session)
                    return
                else:
                    # send them some hints about how to respond
                    if state.question.error_response:
                        response = state.question.error_response
                    else:
                        flat_answers = " or ".join([trans.answer.helper_text() for trans in transitions])
                        # Make translation happen all at the end.  This is currently more practical
                        #translated_answers = _(flat_answers, get_language_code(session.connection))
                        #response = _('"%(answer)s" is not a valid answer. You must enter %(hint)s', 
                        #             get_language_code(session.connection))% ({"answer" : msg.text, "hint": translated_answers})
                        response ='"%(answer)s" is not a valid answer. You must enter ' + flat_answers
                    
                    msg.respond(response, {"answer":msg.text})
                    
                    # update the number of times the user has tried
                    # to answer this.  If they have reached the 
                    # maximum allowed then end their session and
                    # send them an error message.
                    session.num_tries = session.num_tries + 1
                    if state.num_retries and session.num_tries >= state.num_retries:
                        session.state = None
                        msg.respond("Sorry, invalid answer %(retries)s times. Your session will now end. Please try again later.", 
                                    {"retries": session.num_tries })
                        
                    session.save()
                    return True
            
            # create an entry for this response
            # first have to know what sequence number to insert
            ids = Entry.objects.all().filter(session=session).order_by('sequence_id').values_list('sequence_id', flat=True)
            if ids:
                # not sure why pop() isn't allowed...
                sequence = ids[len(ids) -1] + 1
            else:
                sequence = 1
            entry = Entry(session=session,sequence_id=sequence,transition=found_transition,text=msg.text)
            entry.save()
            self.debug("entry %s saved" % entry)
                
            # advance to the next question, or remove
            # this caller's state if there are no more
            
            # this might be "None" but that's ok, it will be the 
            # equivalent of ending the session
            session.state = found_transition.next_state
            session.num_tries = 0
            session.save()
            
            # if this was the last message, end the session, 
            # and also check if the tree has a defined 
            # completion text and if so send it
            if not session.state:
                if session.tree.completion_text:
                    msg.respond(session.tree.completion_text)
                else:
                    official_name = Report.objects.get(session=session).official_name
                    location = Report.objects.get(session=session).location
                    count = Report.objects.filter(official_name=official_name, location=location).count()
                    msg.respond(_("Thank you for reporting this incident. You and %s other people have reported on %s in %s.") % (count,official_name,location))

                # end the connection so the caller can start a new session
                self._end_session(session)
                
            # if there is a next question ready to ask
            # send it along
            self._send_question(session, msg)
            # if we haven't returned long before now, we're
            # long committed to dealing with this message
            return True
    
    def start_tree(self, tree, connection, msg=None):
        '''Initiates a new tree sequence, terminating any active sessions'''
        self.end_sessions(connection)
        session = Session(connection=connection, 
                          tree=tree, state=tree.root_state, num_tries=0)
        session.save()
        self.debug("new session %s saved" % session)
        
        # also notify any session listeners of this
        # so they can do their thing
        if self.session_listeners.has_key(tree.trigger):
            for func in self.session_listeners[tree.trigger]:
                func(session, False)
        self._send_question(session, msg)
    
    def _send_question(self, session, msg=None):
        '''Sends the next question in the session, if there is one''' 
        state = session.state
        if state and state.question:
            response = state.question.text
            self.info("Sending: %s" % response)
            if msg:
                msg.respond(response)
            else:
                # we need to get the real backend from the router 
                # to properly send it 
                real_backend = self.router.get_backend(session.connection.backend.slug)
                if real_backend:
                    connection = Connection(real_backend, session.connection.identity)
                    outgoing_msg = OutgoingMessage(connection, response)
                    self.router.outgoing(outgoing_msg)
                else: 
                    # todo: do we want to fail more loudly than this?
                    error = "Can't find backend %s.  Messages will not be sent" % connection.backend.slug
                    self.error(error)

    def _end_session(self, session, canceled=False):
        '''Ends a session, by setting its state to none,
           and alerting any session listeners'''
        session.state = None
        session.canceled = canceled
        session.save()
        if self.session_listeners.has_key(session.tree.trigger):
            for func in self.session_listeners[session.tree.trigger]:
                func(session, True)
                    
    def end_sessions(self, connection):
        ''' Ends all open sessions with this connection.  
            does nothing if there are no open sessions ''' 
        sessions = Session.objects.filter(connection=connection).exclude(state=None)
        for session in sessions:
            self._end_session(session, True)
            
    def register_custom_transition(self, name, function):
        ''' Registers a handler for custom logic within a 
            state transition '''
        self.info("Registering keyword: %s for function %s" %(name, function.func_name))
        self.registered_functions[name] = function  
        
    def set_session_listener(self, tree_key, function):
        '''Adds a session listener to this.  These functions
           get called at the beginning and end of every session.
           The contract of the function is func(Session, is_ending)
           where is_ending = false at the start and true at the
           end of the session.
        ''' 
        
        self.info("Registering session listener %s for tree %s" %(function.func_name, tree_key))
        # I can't figure out how to deal with duplicates, so only allowing
        # a single registered function at a time.
        #        
        #        if self.session_listeners.has_key(tree_key):
        #            # have to check existence.  This is mainly for the unit tests
        #            if function not in self.session_listeners[tree_key]:
        #                self.session_listeners[tree_key].append(function)
        #        else: 
        self.session_listeners[tree_key] = [function]
        
    def matches(self, answer, message):
        answer_value = message.text
        '''returns True if the answer is a match for this.'''
        if not answer_value:
            return False
        if answer.type == "A":
            return answer_value.lower() == answer.answer.lower()
        elif answer.type == "R":
            return re.match(answer.answer, answer_value, re.IGNORECASE)
        elif answer.type == "C":
            if self.registered_functions.has_key(answer.answer):
                return self.registered_functions[answer.answer](message)
            else:
                raise Exception("Can't find a function to match custom key: %s", answer)
        raise Exception("Don't know how to process answer type: %s", answer.type)
        
        
