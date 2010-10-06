from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory

from goals.models import Goal


class GoalForm(forms.ModelForm):
    apply_schedule = forms.BooleanField(required=False)

    class Meta:
        model = Goal
        fields = ('id',)


GoalFormSet = modelformset_factory(Goal, form=GoalForm, extra=0)


class ScheduleForm(forms.Form):
    start_date = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    frequency = forms.ChoiceField(choices=Goal.REPEAT_CHOICES, required=False)
