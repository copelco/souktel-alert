from django.core.urlresolvers import reverse

from djtables import Table, Column
from djtables.column import DateColumn


class EditLink(Column):
    def __init__(self, name=None, value=None, link=None, sortable=False):
        if not value:
            value = lambda cell: """<img src='/static/group_messaging/edit-icon.jpeg' width='20' height='20' />"""
        super(EditLink, self).__init__(name, value, link, sortable)


class DeleteLink(Column):
    def __init__(self, name=None, value=None, link=None, sortable=False):
        if not value:
            value = lambda cell: """<img src='/static/group_messaging/delete-icon.png' width='20' height='20' />"""
        super(DeleteLink, self).__init__(name, value, link, sortable)


class QuestionTable(Table):

    id = Column()
    text = Column()
    edit = EditLink(link=lambda cell: reverse("insert_question",
                                              args=[cell.row.pk]))
    delete = DeleteLink(link=lambda cell: reverse("delete_question",
                                                  args=[cell.row.pk]))

    class Meta:
        order_by = 'id'
