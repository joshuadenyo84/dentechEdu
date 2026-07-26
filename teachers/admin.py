from django.contrib import admin

from .models import (
    Department,
    Teacher,
    TeacherSubject,
    ClassTeacher
)


class TeacherSubjectInline(admin.TabularInline):
    model = TeacherSubject
    extra = 1


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    list_display = (
        "employee_number",
        "user",
        "department",
        "employment_status",
    )

    search_fields = (
        "employee_number",
        "user__first_name",
        "user__last_name",
        "tsc_number",
    )

    list_filter = (
        "department",
        "employment_status",
    )

    inlines = [
        TeacherSubjectInline,
    ]


admin.site.register(Department)
admin.site.register(ClassTeacher)