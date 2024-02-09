# extracts teachers schedules from data available in regular schedules

import os
import json
from pprint import pprint
from ParseSchedules.models import Lesson, WeeklySchedule

from ParseSchedules.utilities import construct_empty_schedule, merge_classes

path_to_student_schedules = "./output_json"
student_schedules_json: "dict[str, WeeklySchedule]" = {}

# read all json files in the directory and all subdirectories
for root, dirs, files in os.walk(path_to_student_schedules):
    for file in files:
        if file.endswith(".json"):
            print(os.path.join(root, file))

            # open the file using a context manager
            with open(os.path.join(root, file), "r", encoding="utf8") as f:
                # read the file
                data = f.read()

            # parse the json
            parsed_json: WeeklySchedule = json.loads(data)

            #  get file name without extension
            file_name = os.path.splitext(file)[0]

            student_schedules_json[file_name] = parsed_json

# iterate over all student schedules and extract all teachers into a set

teachers: "set[str]" = set()
for schedule_name, schedule_data in student_schedules_json.items():
    for day in schedule_data.keys():
        lessons: list[Lesson] = schedule_data[day]["classes"]
        for lesson in lessons:
            should_add_teacher = lesson.teacher is not None

            if should_add_teacher:
                if "|" in lesson.teacher:
                    # split by pipe and iterate
                    teachers_list = lesson.teacher.split("|")
                    teachers.update(teachers_list)

                else:
                    teachers.add(lesson.teacher)


print(teachers)
print(len(teachers))

# given a teacher, construct teacher schedule
teacher_name_to_schedule_mapping = {
    teacher: construct_empty_schedule() for teacher in teachers
}

for schedule_name, schedule_data in student_schedules_json.items():
    day: str
    for day in schedule_data.keys():
        lessons: list[Lesson] = schedule_data[day]["classes"]
        for lesson in lessons:
            teacher = lesson.teacher
            has_at_least_one_teacher = teacher is not None
            has_several_teachers = has_at_least_one_teacher and "|" in teacher

            if has_at_least_one_teacher:
                # include group name in the lesson
                lesson["group"] = schedule_name

                # helper function to get day classes from teacher's schedule
                get_day_classes = lambda teacher: teacher_name_to_schedule_mapping[
                    teacher
                ][day]["classes"]

                if has_several_teachers:
                    # split by pipe and iterate
                    teachers_list = teacher.split("|")
                    for teacher in teachers_list:
                        get_day_classes(teacher).append(lesson)
                else:
                    # otherwise just add the lesson to the teacher's schedule
                    get_day_classes(teacher).append(lesson)

# merge classes with same index, name and week. The final class should combine groups from each class
for teacher, schedule in teacher_name_to_schedule_mapping.items():
    for day in schedule.keys():
        schedule[day]["classes"] = merge_classes(schedule[day]["classes"])


# sort classes by index
for teacher, schedule in teacher_name_to_schedule_mapping.items():
    for day in schedule.keys():
        schedule[day]["classes"].sort(key=lambda c: c["index"])


# save teacher schedules to json files. The file name should be the teacher's name
for teacher, schedule in teacher_name_to_schedule_mapping.items():
    # construct file name
    file_name = teacher + ".json"

    # open the file
    f = open(os.path.join("./teachers_output_json", file_name), "w", encoding="utf8")

    # write the json
    f.write(json.dumps(schedule, ensure_ascii=False, indent=4))

    # close the file
    f.close()

pprint(teacher_name_to_schedule_mapping["Шепіта"])
