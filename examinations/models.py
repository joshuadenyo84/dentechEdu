from django.db import models
from school.models import School
from academics.models import AcademicYear, Term, Grade, Subject
from students.models import Student
# ❌ Bad
# from academics.models import Grade
# grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

# ✅ Good
grade = models.ForeignKey('academics.Grade', on_delete=models.CASCADE)
class ExamType(models.Model):
    """Defines evaluation blocks (e.g., Opener, Mid-Term, End of Term, KPSEA Mock)"""
    name = models.CharField(max_length=100) # e.g., Mid-Term Assessment
    code = models.CharField(max_length=20, unique=True) # e.g., MID-TERM
    
    def __str__(self):
        return self.name

class ExamSchedule(models.Model):
    """Bridges timetables and terms together to hold structural marks parameters"""
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    max_marks = models.IntegerField(default=100) # Total out of e.g. 100 or 50
    pass_marks = models.IntegerField(default=40)
    exam_date = models.DateField()

    def __str__(self):
        return f"{self.grade} - {self.subject} ({self.exam_type.code})"

class ExamResult(models.Model):
    """Stores the specific marks graded for individual students"""
    schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('schedule', 'student') # Prevents double grading sheets entry

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.schedule.subject}: {self.marks_obtained}"

# Inside examinations/models.py

class ExamResult(models.Model):
    schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('schedule', 'student')

    # Update this method to look like this:
    def __str__(self):
        return f"{self.student.full_name} - {self.schedule.subject}: {self.marks_obtained}"
