# extracts teachers schedules from data available in regular schedules

import os
import json

path_to_student_schedules = "./output_json"
student_schedules_json = {}

# read all json files in the directory and all subdirectories
for root, dirs, files in os.walk(path_to_student_schedules):
    for file in files:
        if file.endswith(".json"):
            print(os.path.join(root, file))

            # TODO: refactor to context manager
            # open the file
            f = open(os.path.join(root, file), "r", encoding="utf8")
            # read the file
            data = f.read()
            # close the file
            f.close()

            # parse the json
            parsed_json = json.loads(data)

            #  get file name without extension
            file_name = os.path.splitext(file)[0]

            student_schedules_json[file_name] = parsed_json

# iterate over all student schedules and extract all teachers into a set
# sample schedule json:
# {
#     "monday": {
#         "classes": [
#             {
#                 "index": 3,
#                 "name": "ТПВ",
#                 "room": "Л.2",
#                 "qualification": "ст. в.",
#                 "teacher": "Снігур",
#                 "label": 2.0,
#                 "isBiweekly": true,
#                 "week": 2
#             },
#             {
#                 "index": 4,
#                 "name": "Технологія поліграфічного виробництва (ТПВ)",
#                 "room": "Л.2",
#                 "qualification": "ст. в.",
#                 "teacher": "Снігур",
#                 "label": 1.0,
#                 "isBiweekly": true,
#                 "week": 1
#             }
#         ]
#     },
teachers = set()
for schedule_name, schedule_data in student_schedules_json.items():
    for day in schedule_data.keys():
        for lesson in schedule_data[day]["classes"]:
            should_add_teacher = lesson["teacher"] is not None

            if should_add_teacher:
                if "|" in lesson["teacher"]:
                    # split by pipe and iterate
                    teachers_list = lesson["teacher"].split("|")
                    teachers.update(teachers_list)

                else:
                    teachers.add(lesson["teacher"])


print(teachers)
print(len(teachers))

# given a teacher, find all the lessons they teach
teacher_lessons_mapping = {teacher: [] for teacher in teachers}

for schedule_name, schedule_data in student_schedules_json.items():
    for day in schedule_data.keys():
        for lesson in schedule_data[day]["classes"]:
            has_teacher = lesson["teacher"] is not None
            has_several_teachers = has_teacher and "|" in lesson["teacher"]

            if has_teacher:
                # include group name in the lesson
                lesson["group"] = schedule_name

                if has_several_teachers:
                    # split by pipe and iterate
                    teachers_list = lesson["teacher"].split("|")
                    for teacher in teachers_list:
                        teacher_lessons_mapping[teacher].append(lesson)
                else:
                    teacher_lessons_mapping[lesson["teacher"]].append(lesson)

print(teacher_lessons_mapping["Шепіта"])
