from django.contrib import admin
from .models import ExamType, ExamSchedule, ExamResult

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('grade', 'subject', 'exam_type', 'term', 'max_marks', 'exam_date')
    list_filter = ('grade', 'exam_type', 'term', 'academic_year')
    search_fields = ('subject__name', 'grade__name')

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_subject', 'get_exam_type', 'marks_obtained')
    list_filter = ('schedule__grade', 'schedule__exam_type', 'schedule__term')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__admission_number')

    # Custom methods to safely extract related structural query data points inside display lists
    def get_subject(self, obj):
        return obj.schedule.subject.name
    get_subject.short_description = 'Subject'

    def get_exam_type(self, obj):
        return obj.schedule.exam_type.name
    get_exam_type.short_description = 'Exam Type'
