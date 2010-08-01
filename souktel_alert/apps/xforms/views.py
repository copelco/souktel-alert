from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError

from rapidsms.utils import render_to_response
from .models import XForm, XFormSubmission, XFormField, XFormFieldConstraint
from xml.dom.minidom import parse, parseString

# CSV Export
@require_GET
def submissions_as_csv(req, pk):
    xform = get_object_or_404(XForm, pk=pk)

    submissions = xform.submissions.all().order_by('-pk')
    fields = xform.fields.all().order_by('pk')

    resp = render_to_response(req, "xforms/submissions.csv", {'xform': xform, 'submissions': submissions, 'fields': fields}, mimetype="text/csv")
    resp['Content-Disposition'] = 'attachment;filename="%s.csv"' % xform.keyword
    return resp

# ODK Endpoints
@require_GET
def odk_list_forms(req):
    xforms = XForm.objects.all().filter(active=True)
    return render_to_response(req, "xforms/odk_list_forms.xml", { 'xforms': xforms, 'host':  settings.XFORMS_HOST }, mimetype="application/xml")

@require_GET
def odk_get_form(req, pk):
    xform = get_object_or_404(XForm, pk=pk)
    resp = render_to_response(req, "xforms/odk_get_form.xml", { 'xform': xform }, mimetype="application/xml")
    resp['Content-Disposition'] = 'attachment;filename="%s.xml"' % xform.keyword
    return resp

@require_POST
def odk_submission(req):
    values = {}
    xform = None
    raw = ""

    for file in req.FILES.values():
        raw = "%s %s" % (raw, file.file.getvalue())
        dom = parseString(file.file.getvalue())
        root = dom.childNodes[0]
        for child in root.childNodes:
            tag = child.tagName
            if child.childNodes:
                body = child.childNodes[0].wholeText
            
                if tag == 'xform-keyword':
                    xform = get_object_or_404(XForm, keyword=body)
                else:
                    values[tag] = body

    # if we found the xform
    submission = xform.process_odk_submission(raw, values)

    resp = render_to_response(req, "xforms/odk_submission.xml", { "xform": xform, "submission": submission })

    # ODK needs two things for a form to be considered successful
    # 1) the status code needs to be 201 (created)
    resp.status_code = 201

    # 2) The location header needs to be set to the host it posted to
    resp['Location'] = "http://%s/submission" % settings.XFORMS_HOST
    return resp


@require_GET
def xforms(req): 
    xforms = XForm.objects.all()
    breadcrumbs = (('XForms', ''),)
    return render_to_response(req, "xforms/form_index.html", { 'xforms': xforms, 'breadcrumbs': breadcrumbs } )

class NewXFormForm(forms.ModelForm): # pragma: no cover
    class Meta:
        model = XForm
        fields = ('name', 'keyword', 'description', 'response')

class EditXFormForm(forms.ModelForm): # pragma: no cover
    class Meta:
        model = XForm
        fields = ('name', 'keyword', 'description', 'response', 'active')

def new_xform(req):
    if req.method == 'POST':
        form = NewXFormForm(req.POST)
        if form.is_valid():
            # create our XForm
            xform = form.save(commit=False)

            # set the user
            xform.owner = req.user

            # commit it
            xform.save()

            return redirect("/xforms/%d/view/" % xform.pk)
    else:
        form = NewXFormForm()

    return render_to_response(req, "xforms/form_create.html", { 'form': form } )


def view_form(req, form_id):
    xform = XForm.objects.get(pk=form_id)
    fields = XFormField.objects.order_by('order').filter(xform=xform)
    breadcrumbs = (('XForms', '/xforms'),('Edit Form', ''))
    return render_to_response(req, "xforms/form_view.html", { 'xform': xform, 'fields': fields, 'field_count' : len(fields), 'breadcrumbs' : breadcrumbs })

def view_form_details(req, form_id):
    xform = XForm.objects.get(pk=form_id)
    return render_to_response(req, "xforms/form_details.html", { 'xform': xform })

def edit_form(req, form_id):
    xform = XForm.objects.get(pk=form_id)
    fields = XFormField.objects.order_by('order').filter(xform=xform)

    breadcrumbs = (('XForms', '/xforms'),('Edit Form', ''))

    if req.method == 'POST':
        form = EditXFormForm(req.POST, instance=xform)
        if form.is_valid():
            xform = form.save()
            return render_to_response(req, "xforms/form_details.html", {"xform" : xform})
    else:
        form = EditXFormForm(instance=xform)

    return render_to_response(req, "xforms/form_edit.html", { 'form': form, 'xform': xform, 'fields': fields, 'field_count' : len(fields), 'breadcrumbs' : breadcrumbs })


def order_xform (req, form_id):
    if req.method == 'POST':
        field_ids = req.POST['order'].split(',')
        count = 1
        for field_id in field_ids:
            field = XFormField.objects.get(pk=field_id)
            field.order = count
            count = count + 1
            field.save()
            
        return render_to_response(req, "xforms/ajax_complete.html", {'ids' : field_ids})

class FieldForm(forms.ModelForm):
    class Meta:
        model = XFormField
        fields = ('type', 'caption', 'command', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }

class ConstraintForm(forms.ModelForm):
    class Meta:
        model = XFormFieldConstraint
        fields = ('type', 'test', 'message') # Why do we need order?
        
def add_field(req, form_id):
    xform = XForm.objects.get(pk=form_id)
    fields = XFormField.objects.filter(xform=xform)

    if req.method == 'POST':
        form = FieldForm(req.POST)
        if form.is_valid():
            field = form.save(commit=False)
            field.xform = xform
            field.order = len(fields)
            field.save()
            return render_to_response(req, "xforms/field_view.html", {'field' : field, 'xform' : xform })
    else:
        form = FieldForm()

    return render_to_response(req, "xforms/field_edit.html", { 'form': form, 'xform': xform })

def view_submissions(req, form_id):
    xform = XForm.objects.get(pk=form_id)

    submissions = xform.submissions.all().order_by('-pk')
    fields = xform.fields.all().order_by('pk')

    breadcrumbs = (('XForms', '/xforms'),('Submissions', ''))
    
    return render_to_response(req, "xforms/submissions.html", { 'xform': xform, 'fields': fields, 'submissions': submissions, 'breadcrumbs': breadcrumbs })

def make_submission_form(xform):
    fields = {}
    for field in xform.fields.all().order_by('order'):
        fields[field.command] = forms.CharField(required=False,
                                                help_text=field.description,
                                                label = field.caption)

    # this method overloads Django's form clean() method and makes sure all the fields
    # pass the constraints determined by our XForm.  This guarantees that even the Admin
    # can't create forms that violate the constraints they set
    def clean(self):
        cleaned_data = self.cleaned_data

        for field in xform.fields.all():
            command = field.command
            if command in cleaned_data:
                field_val = str(cleaned_data.get(command))

                try:
                    cleaned_val = field.clean(field_val)
                except ValidationError as err:
                    # if there is an error, remove it from our cleaned data and 
                    # add the error to our list of errors for this form
                    self._errors[field.command] = (self.error_class(err))
                    del cleaned_data[field.command]

        return cleaned_data

    # super neato Python magic to create a new class dynamically
    #  - first arg is the class name
    #  - second arg is the base class
    #  - third arg is the fields for the class
    return type('SubmissionForm', (forms.BaseForm,), { 'base_fields': fields, 'xform': xform, 'clean': clean })


def edit_submission(req, submission_id):
    submission = get_object_or_404(XFormSubmission, pk=submission_id)
    xform = submission.xform
    fields = xform.fields.all().order_by('order')
    values = submission.values.all()

    form_class = make_submission_form(xform)
    if req.method == 'POST':
        form = form_class(req.POST)

        # no errors?  save and redirect
        if form.is_valid():
            # update our submission
            xform.update_submission_from_dict(submission, form.cleaned_data)

            # redirect to the xform submission page
            return redirect("/xforms/%d/submissions" % xform.pk)
    else:
        # our hash of bound values
        form_vals = {}
        for value in values:
            form_vals[value.field.command] = value.value
        print form_vals

        form = form_class(form_vals)

    breadcrumbs = (('XForms', '/xforms'),('Submissions', '/xforms/%d/submissions' % xform.pk), ('Edit Submission', ''))

    return render_to_response(req, "xforms/submission_edit.html", { 'xform': xform, 'submission': submission,
                                                                    'fields': fields, 'values': values, 'form': form,
                                                                    'breadcrumbs': breadcrumbs })

def view_field(req, form_id, field_id):
    xform = XForm.objects.get(pk=form_id)
    field = XFormField.objects.get(pk=field_id)
    return render_to_response(req, "xforms/field_view.html", { 'xform': xform, 'field' : field })
    

def edit_field (req, form_id, field_id):
    xform = XForm.objects.get(pk=form_id)
    field = XFormField.objects.get(pk=field_id)
    
    if req.method == 'POST':
        form = FieldForm(req.POST, instance=field)
        if form.is_valid():
            field = form.save(commit=False)
            field.xform = xform
            field.save()
            return render_to_response(req, "xforms/field_view.html", { 'form' : form, 'xform' : xform, 'field' : field })
        else:            return render_to_response(req, "xforms/field_edit.html", { 'form' : form, 'xform': xform, 'field' : field })
    else:
        form = FieldForm(instance=field)

    return render_to_response(req, "xforms/field_edit.html", { 'form' : form, 'xform': xform, 'field' : field })


def delete_xform (req, form_id):
    xform = XForm.objects.get(pk=form_id)
    if req.method == 'POST':
        xform.delete()
        
    return redirect("/xforms")

def delete_field (req, form_id, field_id):
    xform = XForm.objects.get(pk=form_id)
    field = XFormField.objects.get(pk=field_id)

    if req.method == 'POST':
        field.delete()
        
    return redirect("/xforms/%d/edit/" % xform.pk)

def add_constraint(req, form_id, field_id):
    xform = XForm.objects.get(pk=form_id)
    field = XFormField.objects.get(pk=field_id)
    constraints = XFormFieldConstraint.objects.order_by('order').filter(field=field)
    form = ConstraintForm()

    if req.method == 'POST':
        form = ConstraintForm(req.POST)
        if form.is_valid():
            constraint = form.save(commit=False)
            constraint.field = field
            constraint.order = len(constraints)
            constraint.save()
            return render_to_response(req, "xforms/table_row_view.html", {'item' : constraint, 'columns': constraint_columns, 'buttons' : constraint_buttons, 'field' : field, 'xform' : xform })
    else:
        form = ConstraintForm()

    return render_to_response(req, "xforms/table_row_edit.html", { 'buttons' : add_button, 'form' : form, 'xform' : xform, 'field' : field });

def edit_constraint(req, form_id, field_id, constraint_id) :
    
    xform = XForm.objects.get(pk=form_id)
    field = XFormField.objects.get(pk=field_id)
    constraint = XFormFieldConstraint.objects.get(pk=constraint_id)
    
    if req.method == 'POST':
        form = ConstraintForm(req.POST, instance=constraint)
        if form.is_valid():
            constraint = form.save(commit=False)
            constraint.field = field
            constraint.save()
            return render_to_response(req, "xforms/table_row_view.html", {  'columns' : constraint_columns, 'buttons' : constraint_buttons, 'item' : constraint, 'form' : form, 'xform' : xform, 'field' : field })
        else:
            return render_to_response(req, "xforms/table_row_edit.html", { 'buttons' : save_button, 'item' : constraint, 'form' : form, 'xform' : xform, 'field' : field })
    else:
        form = ConstraintForm(instance=constraint)
    
    return render_to_response(req, "xforms/table_row_edit.html", { 'buttons' : save_button, 'form' : form, 'xform': xform, 'field' : field, 'item' : constraint })

def view_constraint(req, form_id, field_id, constraint_id) :
    
    xform = XForm.objects.get(pk=form_id)
    field = XFormField.objects.get(pk=field_id)
    constraint = XFormFieldConstraint.objects.get(pk=constraint_id)
    return render_to_response(req, "xforms/table_row_view.html", { 'columns' : constraint_columns, 'buttons' : constraint_buttons, 'item' : constraint, 'xform' : xform, 'field' : field })
    
    
def view_constraints(req, form_id, field_id):
    xform = XForm.objects.get(pk=form_id)
    field = XFormField.objects.get(pk=field_id)
    constraints = XFormFieldConstraint.objects.order_by('order').filter(field=field)

    breadcrumbs = (('XForms', '/xforms'),(xform.name, "/xforms/%s/view/" % xform.pk), ("Constraints", ''))

    return render_to_response(req, "xforms/constraints.html", {  'xform' : xform, 'field' : field, 'table' : constraints, 'buttons' : constraint_buttons, 'columns' : constraint_columns, 'breadcrumbs': breadcrumbs })

def delete_constraint (req, form_id, field_id, constraint_id):
    constraint = XFormFieldConstraint.objects.get(pk=constraint_id)
    if req.method == 'POST':
        constraint.delete()
        
    return redirect("/xforms/%s/field/%s/constraints/" % (form_id, field_id))

def order_constraints (req, form_id, field_id):
    if req.method == 'POST':
        constraint_ids = req.POST['order'].split(',')
        count = 1
        for constraint_id in constraint_ids:
            constraint = XFormFieldConstraint.objects.get(pk=constraint_id)
            constraint.order = count
            count = count + 1
            constraint.save()
            
        return render_to_response(req, "xforms/ajax_complete.html", {'ids' : constraint_ids})


add_button = ({ "image" : "rapidsms/icons/silk/decline.png", 'click' : 'cancelAdd'}, 
              { "text" : "Add", "image" : "rapidsms/icons/silk/add.png", 'click' : 'add'},)

save_button = ( { "image" : "rapidsms/icons/silk/decline.png", 'click' : 'cancelSave'},
                { "text" : "Save", "image" : "xforms/icons/silk/bullet_disk.png", 'click' : 'saveRow'},)
constraint_buttons = ({"image" : "rapidsms/icons/silk/delete.png", 'click' : 'deleteRow'},
                      { "text" : "Edit", "image" : "xforms/icons/silk/pencil.png", 'click' : 'editRow'},)
constraint_columns = (('Type', 'type'), ('Test', 'test'), ('Message', 'message'))


