#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import logging

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response ,redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from groupmessaging.decorators import contact_required
from decisiontree.forms import *
from decisiontree.models import *

from StringIO import StringIO

import csv

def index(req):
    allTrees = Tree.objects.all()
    tree_count = Tree.objects.count()
    
    context_instance=RequestContext(req)
    if len(allTrees) != 0:
        t = allTrees[len(allTrees) - 1]
        context_instance["trees"] = allTrees
        context_instance["t"] = t
        context_instance["total"] = tree_count
        return render_to_response("tree/index.html", context_instance)
    else:
		return render_to_response("tree/index.html", context_instance)

def data(req, id = None):
    allTrees = Tree.objects.all()
    # ok, the plan is to generate a table of responses per state, but this is tricky with loops.
    # the first thing we'll do is get all the possible states you can reach from the tree
    # then we'll tabulate the results of each state's first value
    # then we'll look at paths, by using the concatenated list of states taken for that path as a key
    if len(allTrees) != 0:
        t = get_tree(id)
        all_states = t.get_all_states()
        loops = t.has_loops() 
        if not loops:
            # this is the easy case.  just create one column per state and then display the results
            sessions = Session.objects.all().filter(tree=t)
            return render_to_response("tree/data.html",
                                      RequestContext(req, { "trees": allTrees, "t": t, "states" : all_states, "sessions" : sessions, "loops" : loops}
                                      ))
        else: 
            # here what we want is a table where the columns are every unique path through the 
            # tree, and the rows are the sessions, with the paths filled in.
            # Since there are loops we have to generate the list of unique paths from
            # the session data.  
            # So we get every session, and for every entry in that session we get the path.
            # If we haven't seen the path we add it to the master list.  
            # Then we walk back through the master list, and walk through each session to
            # see if it has an entry matching that path, and if so set the answer.  
            sessions = Session.objects.all().filter(tree=t)
            paths = {}
            # i think paths will be a dictionary of paths to dictionaries of sessions to answers
            # e.g. { <path> : { <session> : <answer>}
            # which will allow us to iterate through paths and say:
            # if paths[path].has_key(session):
            #    this_cell = paths[path][session]
            for session in sessions:
                entries = session.entry_set.all().order_by('sequence_id')
                path = ''
                for entry in entries:
                    path = path + str(entry.transition.current_state.id) + '/'
                    entry.path = path
                    if paths.has_key(path):
                        paths[path][session] = entry.transition.answer
                    else:
                        paths[path] = { session : entry.transition.answer }
            return render_to_response("tree/data.html",
                                      RequestContext(req, { "trees": allTrees, "t": t, "paths" : paths, "sessions" : sessions, "loops" : loops }
                                      ))
        # now we need to map all states to answers
        states_w_answers = {}
        for state in all_states:
            states_w_answers[state] = map((lambda x: x.answer), state.transition_set.all()) 
        # now we need to get all the entries
        all_entries = Entry.objects.all().filter(session__tree = t)
        if loops:
            # stupid error fix to prevent trees with loops from exploding.  This should be done better
            t = Tree()
            t.trigger = "Sorry, can't display this tree because it has loops.  We're working on it."
        return render_to_response("tree/index.html",
            RequestContext(req, { "trees": allTrees, "t": t }))
    else:
        return render_to_response("tree/index.html",
            context_instance=RequestContext(req))

def export(req, id = None):
    t = get_tree(id)
    all_states = t.get_all_states()
    loops = t.has_loops() 
    if not loops:
        output = StringIO()
        w = csv.writer(output)
        headings = ["Person", "Date"]
        headings.extend([state.question for state in all_states])
        w.writerow(headings)
        sessions = Session.objects.all().filter(tree=t)
        for session in sessions:
            values = [str(session.person), session.start_date]
            transitions = map((lambda x: x.transition), session.entry_set.all())
            states_w_transitions = {}
            for transition in transitions:
                states_w_transitions[transition.current_state] = transition
            for state in all_states:
                if states_w_transitions.has_key(state):
                    values.append(states_w_transitions[state].answer)
                else:
                    values.append("")
            w.writerow(values)
        # rewind the virtual file
        output.seek(0)
        response = HttpResponse(output.read(),
                            mimetype='application/ms-excel')
        response["content-disposition"] = "attachment; filename=%s.csv" % t.trigger
        return response
    else:
        return render_to_response("tree/index.html", request_context=RequestContext(req))

def get_tree(id):
    '''Gets a tree.  If id is specified it gets the tree with that Id.
       If Id is not specified it gets the latest tree.  If there are 
       no trees, it returns an empty tree.'''
    if id:
        return Tree.objects.get(id=id)
    else:
        if len(Tree.objects.all()) > 0:
            return Tree.objects.all()[len(Tree.objects.all()) - 1]
        else:
            return Tree()  
    

@contact_required
def addtree(request, treeid=None):
    validationMsg = ""
    tree = None
    if treeid:
        tree = get_object_or_404(Tree, pk=treeid)

    if request.method == 'POST':
        form = TreesForm(request.POST, instance=tree)
        if form.is_valid():
            tree = form.save()
            if treeid:
                validationMsg =("You have successfully updated the Survey")
            else:
                validationMsg = "You have successfully inserted a Survey %s." % tree.trigger
                mycontext = {'validationMsg':validationMsg}
                context = (mycontext)
                return redirect(index)
    else:
        if tree:
            data = {'trigger':tree.trigger,'root_state':tree.root_state,'completion_text':tree.completion_text}
        else:
            data = {'trigger': '', 'root_state': '', 'completion_text': ''}
        form = TreesForm(data)

    mycontext = {'tree':tree, 'form':form, 'validationMsg':validationMsg}
    context = (mycontext)
    return render_to_response('tree/survey.html', context,
                              context_instance=RequestContext(request))

@contact_required
def deletetree(request, treeid):

    tree = Tree.objects.get(id=treeid)
    tree.delete()
    mycontext = {'tree': tree}
    context = (mycontext)

    return redirect(index)

@contact_required
def addquestion(request ,context ,questionid=None):

    validationMsg = ""
    question = None
    if questionid:
           question = get_object_or_404(Question, pk=questionid)
    

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            if questionid:
                validationMsg =("You have successfully updated the Question")
            else:                   
                validationMsg = "You have successfully inserted a Question %s." % question.text
                mycontext = {'validationMsg':validationMsg}                
                context = (mycontext)
                return redirect(questionlist)

    else:
        if question:
            data = {'text':question.text,'error_response':question.error_response}
        else:
            data = {'text': '', 'error_response': ''}
        form = QuestionForm(data)

    if not questionid:
        questionid = 0

    mycontext = {'question':question,'form':form, 'questionid': questionid,'validationMsg':validationMsg}
    context = (mycontext)
    return render_to_response('tree/question.html', context,
                              context_instance=RequestContext(request))


def questionlist(req):
    allQuestions = Question.objects.all()
    questions_count = Question.objects.count()

    context_instance=RequestContext(req)
    if len(allQuestions) != 0:
        q = allQuestions[len(allQuestions) - 1]
        context_instance["questions"] = allQuestions
        context_instance["q"] = q
        context_instance["qtotal"] = questions_count
        return render_to_response("tree/questions_list.html", context_instance)
    else:
		return render_to_response("tree/questions_list.html", context_instance)

@contact_required
def deletequestion(request, questionid):

    question = Question.objects.get(id=questionid)
    question.delete()
    mycontext = {'question': question}
    context = (mycontext)

    return redirect(questionlist)