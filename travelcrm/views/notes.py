# -*-coding: utf-8-*-

import logging
import colander

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ..models import DBSession
from ..models.note import Note
from ..lib.qb.notes import NotesQueryBuilder
from ..lib.utils.resources_utils import get_resource_class
from ..lib.utils.common_utils import translate as _

from ..forms.notes import NoteSchema


log = logging.getLogger(__name__)


class Notes(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        context='..resources.notes.Notes',
        request_method='GET',
        renderer='travelcrm:templates/notes/index.mak',
        permission='view'
    )
    def index(self):
        return {}

    @view_config(
        name='list',
        context='..resources.notes.Notes',
        xhr='True',
        request_method='POST',
        renderer='json',
        permission='view'
    )
    def _list(self):
        qb = NotesQueryBuilder(self.context)
        qb.search_simple(
            self.request.params.get('q')
        )
        id = self.request.params.get('id')
        if id:
            qb.filter_id(id.split(','))
        qb.sort_query(
            self.request.params.get('sort'),
            self.request.params.get('order', 'asc')
        )
        qb.page_query(
            int(self.request.params.get('rows')),
            int(self.request.params.get('page'))
        )
        return {
            'total': qb.get_count(),
            'rows': qb.get_serialized()
        }

    @view_config(
        name='view',
        context='..resources.notes.Notes',
        request_method='GET',
        renderer='travelcrm:templates/notes/form.mak',
        permission='view'
    )
    def view(self):
        if self.request.params.get('rid'):
            resource_id = self.request.params.get('rid')
            note = Note.by_resource_id(resource_id)
            return HTTPFound(
                location=self.request.resource_url(
                    self.context, 'view', query={'id': note.id}
                )
            )
        result = self.edit()
        result.update({
            'title': _(u"View Note"),
            'readonly': True,
        })
        return result

    @view_config(
        name='add',
        context='..resources.notes.Notes',
        request_method='GET',
        renderer='travelcrm:templates/notes/form.mak',
        permission='add'
    )
    def add(self):
        return {
            'title': _(u'Add Note'),
        }

    @view_config(
        name='add',
        context='..resources.notes.Notes',
        request_method='POST',
        renderer='json',
        permission='add'
    )
    def _add(self):
        schema = NoteSchema().bind(request=self.request)
        try:
            controls = schema.deserialize(self.request.params)
            note = Note(
                title=controls.get('title'),
                descr=controls.get('descr'),
                resource=self.context.create_resource()
            )
            DBSession.add(note)
            DBSession.flush()
            return {
                'success_message': _(u'Saved'),
                'response': note.id
            }
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }

    @view_config(
        name='edit',
        context='..resources.notes.Notes',
        request_method='GET',
        renderer='travelcrm:templates/notes/form.mak',
        permission='edit'
    )
    def edit(self):
        note = Note.get(self.request.params.get('id'))
        return {
            'item': note,
            'title': _(u'Edit Note'),
        }

    @view_config(
        name='edit',
        context='..resources.notes.Notes',
        request_method='POST',
        renderer='json',
        permission='edit'
    )
    def _edit(self):
        schema = NoteSchema().bind(request=self.request)
        note = Note.get(self.request.params.get('id'))
        try:
            controls = schema.deserialize(self.request.params)
            note.title = controls.get('title')
            note.descr = controls.get('descr')
            return {
                'success_message': _(u'Saved'),
                'response': note.id
            }
        except colander.Invalid, e:
            return {
                'error_message': _(u'Please, check errors'),
                'errors': e.asdict()
            }

    @view_config(
        name='copy',
        context='..resources.notes.Notes',
        request_method='GET',
        renderer='travelcrm:templates/notes/form.mak',
        permission='add'
    )
    def copy(self):
        note = Note.get(self.request.params.get('id'))
        return {
            'item': note,
            'title': _(u"Copy Note")
        }

    @view_config(
        name='copy',
        context='..resources.notes.Notes',
        request_method='POST',
        renderer='json',
        permission='add'
    )
    def _copy(self):
        return self._add()

    @view_config(
        name='details',
        context='..resources.notes.Notes',
        request_method='GET',
        renderer='travelcrm:templates/notes/details.mak',
        permission='view'
    )
    def details(self):
        note = Note.get(self.request.params.get('id'))
        note_resource = None
        if note.note_resource:
            resource_cls = get_resource_class(
                note.note_resource.resource_type.name
            )
            note_resource = resource_cls(self.request)
        return {
            'item': note,
            'note_resource': note_resource,
        }

    @view_config(
        name='delete',
        context='..resources.notes.Notes',
        request_method='GET',
        renderer='travelcrm:templates/notes/delete.mak',
        permission='delete'
    )
    def delete(self):
        return {
            'title': _(u'Delete Notes'),
            'id': self.request.params.get('id')
        }

    @view_config(
        name='delete',
        context='..resources.notes.Notes',
        request_method='POST',
        renderer='json',
        permission='delete'
    )
    def _delete(self):
        errors = 0
        for id in self.request.params.getall('id'):
            item = Note.get(id)
            if item:
                DBSession.begin_nested()
                try:
                    DBSession.delete(item)
                    DBSession.commit()
                except:
                    errors += 1
                    DBSession.rollback()
        if errors > 0:
            return {
                'error_message': _(
                    u'Some objects could not be delete'
                ),
            }
        return {'success_message': _(u'Deleted')}
