'''Endpoints messages.'''


from protorpc import messages

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

class TextMessage(messages.Message):
    recipient = messages.StringField(1)
    sender = messages.StringField(2)
    from = messages.StringField(3)
    subject = messages.StringField(4)
    body-plain = messages.StringField(5)
    stripped-text = messages.StringField(6)
    stripped-signature = messages.StringField(7)
    body-html = messages.StringField(8)
    stripped-html = messages.StringField(9)
    attachment-count = messages.IntegerField(10)
    timestamp = messaegs.IntegerField(11)
    token = messages.StringField(12)
    signature = messages.StringField(13)
