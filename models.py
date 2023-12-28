from typing import List, Optional


class Lesson:
    def __init__(
        self,
        index: int,
        name: str,
        room: str,
        qualification: str,
        teacher: str,
        label: Optional[float],
        isBiweekly: Optional[bool] = None,
        week: Optional[int] = None,
    ):
        self.index = index
        self.name = name
        self.room = room
        self.qualification = qualification
        self.teacher = teacher
        self.label = label
        self.isBiweekly = isBiweekly
        self.week = week


class DaySchedule:
    def __init__(self, classes: List[Lesson]):
        self.classes = classes


class WeeklySchedule:
    def __init__(
        self,
        monday: DaySchedule,
        tuesday: DaySchedule,
        wednesday: DaySchedule,
        thursday: DaySchedule,
        friday: DaySchedule,
    ):
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
