'''NDB models.'''


from google.appengine.ext import ndb


class Teacher(ndb.Model):
    '''Represents a teacher with associated OAuth account.'''
    user = ndb.UserProperty()
    name_prefix = ndb.StringProperty()
    name_text = ndb.StringProperty()
    profilepic = ndb.StringProperty()

class Student(ndb.Model):
    '''Represents a student with associated OAuth account.'''
    user = ndb.UserProperty()

class StudentID(ndb.Model):
    dsid = ndb.IntegerProperty()
    attendence_status = ndb.IntegerProperty()

class Classroom(ndb.Model):
    '''An individual classroom on a specific date.'''
    teacher = ndb.IntegerProperty()
    room = ndb.StringProperty()
    totalseats = ndb.IntegerProperty()
    takenseats = ndb.ComputedProperty(lambda self: len(self.signedup_students))
    signedup_students = ndb.IntegerProperty(repeated=True)

class Prefs(ndb.Model):
    enable_register_student = ndb.BooleanProperty(default=False)

class Date(ndb.Model):
    '''The date of a tutorial.

    Serves as a parent for Classroom entities.
    '''
    date = ndb.DateProperty(auto_now_add=True)
