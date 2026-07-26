from django.db import models

from academics.models import (
    AcademicYear,
    Term,
    Grade,
    Stream,
    Subject,
)

from teachers.models import Teacher


class SchoolDay(models.Model):
    DAYS = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
    ]

    name = models.CharField(max_length=20, choices=DAYS, unique=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Period(models.Model):
    name = models.CharField(max_length=30)
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.PositiveIntegerField()
    is_break = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(default=40)
    is_special = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TimetableEntry(models.Model):

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)

    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    day = models.ForeignKey(SchoolDay, on_delete=models.CASCADE)

    period = models.ForeignKey(Period, on_delete=models.CASCADE)

    class Meta:
        ordering = ["day", "period"]