'''Decorators that restrict endpoints methods.

This decorator must be applied before the `endpoints.method` decorator.  So:

    @endpoints.method(...)
    @requires_student
    def foo(self, request):
        ...
'''


import endpoints
import google.appengine.api.users
import models
from libs import wrapt
#from google.appengine.ext import ndb

def is_student(user):
    if user is None:
        return None
    student_list = models.Student.query(models.Student.user == user).fetch(1)
    prefs_list = models.Prefs.query().fetch(1)
    if not len(prefs_list):
        new_prefs = models.Prefs()
        new_prefs.put()
        prefs_list = models.Prefs.query().fetch(1)
        print prefs_list
    prefs = prefs_list[0]
    if not len(student_list):
        if prefs.enable_register_student:
            student = models.Student(user=user)
            student.put()
            student_list.append(student)
        else:
            return None
    print student_list
    return student_list[0]

def is_teacher(user):
    if user is None:
        return None
    teacher_list = models.Teacher.query(models.Teacher.user == user).fetch(1)
    if not len(teacher_list):
        return None
    return teacher_list[0]

def is_admin(user):
    if user is None:
        return None
    admin_list = [] # TODO for Sebastian: make datastore object
    if not len(admin_list):
        return None
    return admin_list[0]

def is_root(user):
    if user is None:
        return None
    root_list = ('lord.of.all.sebastian@gmail.com',
                 'zotavka@gmail.com',
                 'drakedevelopersclub@gmail.com')
    for email in root_list:
        if user.email() == email:
            return True
    return None

def auth_requires(allowed, error_message='Invalid token.'):
    '''Return a decorator to require a user to meet specific requirements, else throw a 401.

    Also passes the current user as keyword argument 'current_user'.

    Args:
        allowed (function):
            Accepts a user as an argument, and returns boolean whether the user is valid.
        error_message (str):
            Message to be sent with the 401 should validation fail.
    '''
    @wrapt.decorator
    def decorator(func, instance, args, kwargs):
        current_user = endpoints.get_current_user()
        user_entity = allowed(current_user)
        if is_root(current_user) == None and user_entity == None:
            raise endpoints.UnauthorizedException(error_message)
        kwargs['user_entity'] = user_entity
        return func(*args, **kwargs)
    return decorator

auth_aware = auth_requires(lambda user: True)
requires_student = auth_requires(is_student, 'Invalid token, must be student.')
requires_teacher = auth_requires(lambda user: is_teacher(user) or is_admin(user), 'Invalid token, must be teacher.')
requires_admin = auth_requires(is_admin, 'Invalid token, must be admin.')
requires_root = auth_requires(is_root, 'Invalid token, must be root.')
