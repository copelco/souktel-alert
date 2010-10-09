from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
def mean(values):
    copy = sorted(values)
    size = len(copy)
    if size % 2 == 1:
        return copy[(size - 1) / 2]
    else:
        return (copy[size/2 - 1] + copy[size/2]) / 2


@register.filter
def mode(values):
    copy = sorted(values)
    counts = {}
    for x in set(copy):
        count = copy.count(x)
        if count not in counts:
            counts[count] = []
        counts[count].append(x)
    return counts[max(counts.keys())]


@register.inclusion_tag("tree/partials/tree.html")
def render_tree(tree):
	return { "tree": tree }

@register.inclusion_tag("tree/partials/question.html")
def render_question(question):
	return { "question": question }

@register.inclusion_tag("tree/partials/state.html")
def render_state(state):
    return { "state": state}
