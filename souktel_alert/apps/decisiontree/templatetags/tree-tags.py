from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
def mean(values):
    try:
        integers = [int(v) for v in values]
    except (TypeError, ValueError):
        return 'n/a'
    return sum(integers)/len(integers)*1.0


@register.filter
def median(values):
    try:
        values = [int(v) for v in values]
    except (TypeError, ValueError):
        pass
    values = sorted(values)
    size = len(values)
    try:
        if size % 2 == 1:
            return values[(size - 1) / 2]
        else:
            values = [int(v) for v in values]
            return (values[size/2 - 1] + values[size/2]) / 2
    except (TypeError, ValueError):
        return 'n/a'


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
