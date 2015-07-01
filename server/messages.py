'''Endpoints messages.'''


from protorpc import messages

class State(messages.Enum):
    SUCCESS = 0
    ALREADY_DONE = 1
    CLASS_FULL = 2
    INVALID_ID = 3

class ClassroomQueryMessage(messages.Message):
    date = messages.StringField(1, required=True)
    search = messages.StringField(2)

class ClassroomMessage(messages.Message):
    dsid = messages.StringField(1)
    parent_id = messages.StringField(2)
    teacher = messages.StringField(3)
    profilepic = messages.StringField(4)
    room = messages.StringField(5)
    totalseats = messages.IntegerField(6)
    takenseats = messages.IntegerField(7)
    signedup = messages.BooleanField(8)

class ClassroomListMessage(messages.Message):
    classrooms = messages.MessageField(ClassroomMessage, 1, repeated=True)

class SignupCommandMessage(messages.Message):
    dsid = messages.StringField(1)
    parent_id = messages.StringField(2)
    signup = messages.BooleanField(3)

class SignupStateMessage(messages.Message):
    '''
    Status codes:
        0: Successful
        1: Already Signed Up
        2: Class Full
        3: Invalid ID
    Additional codes can be added as needed.
    '''



    signedup = messages.BooleanField(1)
    status = messages.EnumField(State, 2, default=0)
    message = messages.StringField(3)

class NextTutorialDateMessage(messages.Message):
    date = messages.StringField(1)

class StudentMessage(messages.Message):
    name = messages.StringField(1)

class StudentListMessage(messages.Message):
    students = messages.MessageField(StudentMessage, 1, repeated=True)

class VerifyStudentMessage(messages.Message):
    '''
    Status Codes:
        0: Present
        1: Tardy
        2: Absent
    '''

    class Verification(messages.Enum):
        PRESENT = 0
        TARDY = 1
        ABSENT = 2

    student_id = messages.StringField(1)
    presence_state = messages.EnumField(Verification, 2)

class VerifyStudentMessageResponse(messages.Message):
    status = messages.EnumField(State, 1)

class GetAuthMessage(messages.Message):
    class AuthLevel(messages.Enum):
        NO_USER = 0
        STUDENT = 1
        TEACHER = 2
        ADMIN = 3
        ROOT = 4
    auth = messages.EnumField(AuthLevel, 1)

#New stuff for HAC client

class AssigmentHAC(messages.Message):
    title = messages.StringField(1)
    category = messages.StringField(2)
    date_assigned = messages.StringField(3)
    date_due = messages.StringField(4)
    score = messages.StringField(5)
    max_score = messages.StringField(6)

class GradeHAC(messages.Message):
    category = messages.StringField(1)
    weight = messages.StringField(2)
    score = messages.StringField(3)
    max_score = messages.StringField(4)
    percent = messages.StringField(5)
    weighted_points = messages.StringField(6)

class ClassHAC(messages.Message):
    title = messages.StringField(1)
    assignments = messages.MessageField(AssigmentHAC, 2, repeated=True)
    grade_table = messages.MessageField(GradeHAC, 3, repeated=True)
    grade_percent = messages.StringField(4)
    grade_letter = messages.StringField(5)


class LoginHAC(messages.Message):
    username = messages.StringField(1)
    password = messages.StringField(2)

class ClassesHAC(messages.Message):
    classes = messages.MessageField(ClassHAC, 1, repeated=True)
    class LoginStatus(messages.Enum):
        OK = 0
        LOGIN_ERROR = 1
    status = messages.EnumField(LoginStatus, 2)
