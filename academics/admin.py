from django.contrib import admin
from .models import AcademicYear, Term, Grade, Stream, Subject

from .models import (
    AcademicYear,
    Term,
    Grade,
    Stream,
    Subject,
    GradeSubject,
)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_current")
    list_filter = ("is_current",)
    search_fields = ("name",)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "start_date", "end_date", "is_current")
    list_filter = ("academic_year", "is_current")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("name", "grade")
    list_filter = ("grade",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(GradeSubject)
class GradeSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "grade",
        "subject",
        "weekly_lessons",
        "is_compulsory",
    )

    list_filter = (
        "grade",
        "is_compulsory",
    )

    search_fields = (
        "grade__name",
        "subject__name",
    )    