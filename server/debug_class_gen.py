'''Functions to generate classrooms for debugging.'''


import models


def test_gen_class(next_tutorial, name='Mr. Milstead', profilepic='', room='123', totalseats=12):
    date = models.Date(date=next_tutorial)
    teacher1 = models.Teacher(name_text=name.split()[1], name_prefix=name.split()[0])
    key = date.put()
    class1 = models.Classroom(parent=key, teacher=teacher1, room=room,
                                   totalseats=totalseats,
                                   signedup_students=[])
    class1.put()

def test_gen_classes(next_tutorial):
    classlist = [
            {
              "teacher": "Mr. Milstead",
              "profilepic": "http://cache3.asset-cache.net/gc/57442583-portrait-of-a-school-teacher-gettyimages.jpg?v=1&c=IWSAsset&k=2&d=Y3hy48kuiy7pabQpAfxaQrcgpfAMUuQ1FcwFl8J80Es%3D",
              "room": "127",
              "totalseats": 30,
              "takenseats": 12,
            },
            {
              "teacher": "Mrs. Foo",
              "profilepic": "http://mcauliffe.dpsk12.org/wp-content/uploads/2011/09/StephanieGronholz_Retouch-square-crop.jpg",
              "room": "222",
              "totalseats": 28,
              "takenseats": 28,
            },
            {
              "teacher": "Mr. Bar",
              "profilepic": "http://4.bp.blogspot.com/-sXyOdCbaVi4/UA7dYAwjUCI/AAAAAAAAFmI/tbO4vxpVHS4/s220/nfowkes-square.jpg",
              "room": "409",
              "totalseats": 30,
              "takenseats": 28,
            },
            {
              "teacher": "Mrs. Wolfeschlegelsteinhausenbergerdorff",
              "profilepic": "http://cache2.asset-cache.net/gc/dv1313056-portrait-of-a-mature-teacher-gettyimages.jpg?v=1&c=IWSAsset&k=2&d=jDI%2BiZbzwv%2BjFYTsYAzbzRIz392Wxp0jHzYXiV6NO3k%3D",
              "room": "413",
              "totalseats": 18,
              "takenseats": 17,
            },
            {
              "teacher": "Mrs. Example",
              "profilepic": "http://cache4.asset-cache.net/gc/57442708-portrait-of-a-female-school-teacher-gettyimages.jpg?v=1&c=IWSAsset&k=2&d=E5y3FqGCZA78hfJC8P3s3hrnAf50DBBxD1Fa1hqvjx8%3D",
              "room": "104A",
              "totalseats": 33,
              "takenseats": 0,
            }
          ]
    date = models.Date(date=next_tutorial)
    key = date.put()
    for i in classlist:
        teacher = models.Teacher(name_text=i['teacher'].split()[1],
                             name_prefix=i['teacher'].split()[0],
                             profilepic=i['profilepic'])
        teacher_key = teacher.put()
        teacher_id = teacher_key.id()
        students = []
        for j in range(i['takenseats']):
            student = models.Student()
            student_key = student.put()
            student_id = student_key.id()
            students.append(student_id)
        classroom = models.Classroom(parent=key, teacher=teacher_id, room=i['room'],
                                 totalseats=i['totalseats'], signedup_students=students)
        classroom.put()
