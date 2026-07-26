from django.contrib import admin

from .models import (
    SchoolDay,
    Period,
    Room,
    TimetableEntry,
)


admin.site.register(SchoolDay)
admin.site.register(Period)
admin.site.register(Room)


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):

    list_display = (
        "day",
        "period",
        "grade",
        "stream",
        "subject",
        "teacher",
        "room",
    )

    list_filter = (
        "day",
        "grade",
        "stream",
    )

    search_fields = (
        "teacher__user__first_name",
        "teacher__user__last_name",
        "subject__name",
    )