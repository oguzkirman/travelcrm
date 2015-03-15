# -*-coding: utf-8-*-

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Table,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref

from ..models import (
    DBSession,
    Base,
)
from ..lib import EnumIntType
from ..lib.utils.common_utils import translate as _


task_resource = Table(
    'task_resource',
    Base.metadata,
    Column(
        'task_id',
        Integer,
        ForeignKey(
            'task.id',
            ondelete='restrict',
            onupdate='cascade',
            name='fk_task_id_task_resource',
        ),
        primary_key=True,
    ),
    Column(
        'resource_id',
        Integer,
        ForeignKey(
            'resource.id',
            ondelete='restrict',
            onupdate='cascade',
            name='fk_resource_id_task_resource',
        ),
        primary_key=True,
    )
)


class Task(Base):
    __tablename__ = 'task'

    STATUS = (
        ('new', _(u'new')),
        ('enquiry', _(u'enquiry')),
        ('in_work', _(u'in work')),
        ('ready', _(u'ready')),
    )

    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True
    )
    resource_id = Column(
        Integer,
        ForeignKey(
            'resource.id',
            name="fk_resource_id_task",
            ondelete='restrict',
            onupdate='cascade',
        ),
        nullable=False,
    )
    employee_id = Column(
        Integer,
        ForeignKey(
            'employee.id',
            name="fk_employee_id_task",
            ondelete='restrict',
            onupdate='cascade',
        ),
        nullable=False,
    )
    title = Column(
        String(length=128),
        nullable=False,
    )
    deadline = Column(
        DateTime,
        nullable=False,
    )
    reminder = Column(
        DateTime,
    )
    descr = Column(
        String,
    )
    status = Column(
        EnumIntType(STATUS),
        default='new',
        nullable=False,
    )
    resource = relationship(
        'Resource',
        backref=backref(
            'task',
            uselist=False,
            cascade="all,delete"
        ),
        foreign_keys=[resource_id],
        cascade="all,delete",
        uselist=False,
    )
    task_resource = relationship(
        'Resource',
        secondary=task_resource,
        backref=backref(
            'tasks',
            uselist=True,
            lazy='dynamic',
        ),
        uselist=False,
    )
    employee = relationship(
        'Employee',
        backref=backref(
            'tasks',
            uselist=True,
            lazy="dynamic"
        ),
        uselist=False
    )

    @classmethod
    def get(cls, id):
        if id is None:
            return None
        return DBSession.query(cls).get(id)

    @classmethod
    def by_resource_id(cls, resource_id):
        if resource_id is None:
            return None
        return (
            DBSession.query(cls).filter(cls.resource_id == resource_id).first()
        )

    @property
    def reminder_date(self):
        if self.reminder:
            return self.reminder.date()

    @property
    def reminder_time(self):
        if self.reminder:
            return self.reminder.time()
