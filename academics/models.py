from django.db import models

# ❌ Bad
# from academics.models import Grade
# grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

# ✅ Good
grade = models.ForeignKey('academics.Grade', on_delete=models.CASCADE)
class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class Term(models.Model):
    TERM_CHOICES = [
        ("Term 1", "Term 1"),
        ("Term 2", "Term 2"),
        ("Term 3", "Term 3"),
    ]

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="terms"
    )

    name = models.CharField(max_length=20, choices=TERM_CHOICES)

    start_date = models.DateField()
    end_date = models.DateField()

    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ("academic_year", "name")
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.name} - {self.academic_year}"


class Grade(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Stream(models.Model):
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="streams"
    )

    name = models.CharField(max_length=30)

    class Meta:
        unique_together = ("grade", "name")

    def __str__(self):
        return f"{self.grade} - {self.name}"


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class GradeSubject(models.Model):
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="grade_subjects"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="subject_grades"
    )

    is_compulsory = models.BooleanField(default=True)

    weekly_lessons = models.PositiveIntegerField(default=5)

    class Meta:
        unique_together = ("grade", "subject")
        ordering = ["grade", "subject"]

    def __str__(self):
        return f"{self.grade} - {self.subject}"