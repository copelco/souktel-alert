#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import csv
import logging
from StringIO import StringIO

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response ,redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count

from decisiontree.forms import *
from decisiontree.models import *

from group_messaging.decorators import contact_required


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


@contact_required
def data(request, id):
    tree = get_object_or_404(Tree, pk=id)
    # if req.method == 'POST':
    #     form = AnswerSearchForm(req.POST, tree=tree)
    #     if form.is_valid():
    #         answer = form.cleaned_data['answer']
    #         # what now?
    # else:
    #     form = AnswerSearchForm(tree=tree)

    entry_tags = Entry.tags.through.objects
    entry_tags = entry_tags.filter(entry__session__tree=tree)
    entry_tags = entry_tags.select_related('tag')
    tag_map = {}
    for entry_tag in entry_tags:
        if entry_tag.entry_id not in tag_map:
            tag_map[entry_tag.entry_id] = []
        tag_map[entry_tag.entry_id].append(entry_tag.tag)
    # pre-fetch all entries for this tree and create a map so we can
    # efficiently pair everything up in Python, rather than lots of SQL
    entries = Entry.objects.filter(session__tree=tree).select_related()
    entry_map = {}
    for entry in entries:
        entry.cached_tags = tag_map.get(entry.pk, [])
        state = entry.transition.current_state
        if entry.session.pk not in entry_map:
            entry_map[entry.session.pk] = {}
        entry_map[entry.session.pk][state.pk] = entry
    states = tree.get_all_states()
    sessions = tree.sessions.select_related().order_by('-start_date')
    # for each session, created an ordered list of (state, entry) pairs
    # using the map from above. this will ease template display.
    for session in sessions:
        session.ordered_states = []
        for state in states:
            try:
                entry = entry_map[session.pk][state.pk]
            except KeyError:
                entry = None
            session.ordered_states.append((state, entry))
    # count answers grouped by state
    stats = Transition.objects.filter(entries__session__tree=tree)
    stats = stats.values('current_state', 'answer__answer')
    stats = stats.annotate(count=Count('answer'))
    stat_map = {}
    for stat in stats:
        current_state = stat['current_state']
        answer = stat['answer__answer']
        count = stat['count']
        if current_state not in stat_map:
            stat_map[current_state] = {'answers': {}, 'total': 0}
        stat_map[current_state]['answers'][answer] = count
        stat_map[current_state]['total'] += count
    for state in states:
        state.stats = stat_map.get(state.pk, {})
    context = {
        # 'form': form,
        'tree': tree,
        'sessions': sessions,
        'states': states,
    }
    return render_to_response("tree/data.html", context,
                              context_instance=RequestContext(request))


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
def addquestion(request, questionid=None):
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
            messages.info(request, validationMsg)
            return HttpResponseRedirect(reverse('list-questions'))
    else:
        form = QuestionForm(instance=question)

    context = {
        'question': question,
        'form': form,
        'questionid': questionid,
    }
    return render_to_response('tree/question.html', context,
                              context_instance=RequestContext(request))


@contact_required
def questionlist(request):
    context = {
        'questions': Question.objects.order_by('text')
    }
    return render_to_response('tree/questions_list.html', context,
                              context_instance=RequestContext(request))


@contact_required
def deletequestion(request, questionid):
    tree = get_object_or_404(Question, pk=questionid)
    tree.delete()
    messages.info(request, 'Question successfully deleted')
    return HttpResponseRedirect(reverse('list-questions'))


@contact_required
def addanswer(request, answerid=None):
    answer = None
    if answerid:
           answer = get_object_or_404(Answer, pk=answerid)

    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save()
            if answerid:
                validationMsg =("You have successfully updated the Answer")
            else:
                validationMsg = "You have successfully inserted Answer %s." % answer.answer
                mycontext = {'validationMsg':validationMsg}
            messages.info(request, validationMsg)
            return HttpResponseRedirect(reverse('answer_list'))

    else:
        form = AnswerForm(instance=answer)

    context = {
        'answer': answer,
        'form': form,
        'answerid': answerid,
    }
    return render_to_response('tree/answer.html', context,
                              context_instance=RequestContext(request))


@contact_required
def deleteanswer(request, answerid):
    answer = get_object_or_404(Answer, pk=answerid)
    answer.delete()
    messages.info(request, 'Answer successfully deleted')
    return HttpResponseRedirect(reverse('answer_list'))


@contact_required
def answerlist(request):
    context = {
        'answers': Answer.objects.order_by('name'),
    }
    return render_to_response("tree/answers_list.html", context,
                              context_instance=RequestContext(request))


@contact_required
def list_entries(request):
    """ List most recent survey activity """
    entries = Entry.objects.select_related().order_by('-time')[:25]
    context = {
        'entries': entries,
    }
    return render_to_response("tree/entry/list.html", context,
                              context_instance=RequestContext(request))


@contact_required
def update_entry(request, entry_id):
    """ Manually update survey entry tags """
    entry = get_object_or_404(Entry, pk=entry_id)
    if request.method == 'POST':
        form = EntryTagForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.info(request, 'Tags successfully updated')
            return HttpResponseRedirect(reverse('survey-report',
                                        args=[entry.session.tree.id]))
    else:
        form = EntryTagForm(instance=entry)
    context = {
        'form': form,
        'entry': entry,
    }
    return render_to_response("tree/entry/edit.html", context,
                              context_instance=RequestContext(request))


@contact_required
def addstate(request, stateid=None):

    validationMsg = ""
    state = None
    if stateid:
           state = get_object_or_404(TreeState, pk=stateid)


    if request.method == 'POST':
        form = StateForm(request.POST, instance=state)
        if form.is_valid():
            state = form.save()
            if stateid:
                validationMsg =("You have successfully updated the Question state")
            else:
                validationMsg = "You have successfully inserted State %s." % state.name
                mycontext = {'validationMsg':validationMsg}
                context = (mycontext)
                return redirect(statelist)

    else:
        if state:
            data = {'name':state.name,'question':state.question, 'answer':state.num_retries}
        else:
            data = {'name': '', 'question': '', 'num retries': ''}
        form = StateForm(data)

    if not stateid:
        stateid = 0

    mycontext = {'state':state,'form':form, 'stateid': stateid,'validationMsg':validationMsg}
    context = (mycontext)
    return render_to_response('tree/state.html', context,
                              context_instance=RequestContext(request))

def statelist(req):
    allStates =  TreeState.objects.all()
    states_count =  TreeState.objects.count()

    context_instance=RequestContext(req)
    if len(allStates) != 0:
        s = allStates[len(allStates) - 1]
        context_instance["states"] = allStates
        context_instance["s"] = s
        context_instance["stotal"] = states_count
        return render_to_response("tree/states_list.html", context_instance)
    else:
		return render_to_response("tree/states_list.html", context_instance)


@contact_required
def deletestate(request, stateid):

    state = TreeState.objects.get(id=stateid)
    state.delete()
    mycontext = {'state': state}
    context = (mycontext)

    return redirect(statelist)


@contact_required
def questionpathlist(request):
    paths = Transition.objects.select_related('current_state__question',
                                              'next_state__question',
                                              'answer')
    paths = paths.order_by('current_state__question__text')
    trans_tags = Transition.tags.through.objects
    trans_tags = trans_tags.filter(transition__in=[p.pk for p in paths])
    trans_tags = trans_tags.select_related('tag')
    path_map = {}
    for trans_tag in trans_tags:
        if trans_tag.transition_id not in path_map:
            path_map[trans_tag.transition_id] = []
        path_map[trans_tag.transition_id].append(trans_tag.tag)
    for path in paths:
        path.cached_tags = path_map.get(path.pk, [])
    context = {
        'paths': paths,
    }
    return render_to_response('tree/path_list.html', context,
                              context_instance=RequestContext(request))


@contact_required
def deletepath(request, pathid):

    path = Transition.objects.get(id=pathid)
    path.delete()
    mycontext = {'path': path}
    context = (mycontext)

    return redirect(statelist)

@contact_required
def questionpath(request, pathid=None):
    path = None
    if pathid:
        path = get_object_or_404(Transition, pk=pathid)

    if request.method == 'POST':
        form = PathForm(request.POST, instance=path)
        if form.is_valid():
            path = form.save()
            if pathid:
                validationMsg =("You have successfully updated the Question Path")
            else:
                validationMsg = "You have successfully inserted Question Path %s." % path.id
            messages.info(request, validationMsg)
            return HttpResponseRedirect(reverse('path_list'))
    else:
        form = PathForm(instance=path)

    context = {
        'path': path,
        'form': form,
        'pathid': pathid,
    }
    return render_to_response('tree/path.html', context,
                              context_instance=RequestContext(request))


@contact_required
def list_tags(request):
    context = {
        'tags': Tag.objects.order_by('name'),
    }
    return render_to_response("tree/tags/list.html", context,
                              context_instance=RequestContext(request))


@contact_required
def create_edit_tag(request, tag_id=None):
    tag = None
    if tag_id:
        tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            saved_tag = form.save()
            messages.info(request, 'Tag successfully saved')
            return HttpResponseRedirect(reverse('list-tags'))
    else:
        form = TagForm(instance=tag)
    context = {
        'tag': tag,
        'form': form,
    }
    return render_to_response("tree/tags/edit.html", context,
                              context_instance=RequestContext(request))
