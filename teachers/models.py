from django.db import models
from django.conf import settings

from academics.models import Subject, Stream

# ❌ Bad
# from academics.models import Grade
# grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

# ✅ Good
grade = models.ForeignKey('academics.Grade', on_delete=models.CASCADE)
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Teacher(models.Model):

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
    )

    EMPLOYMENT_STATUS = (
        ("Permanent", "Permanent"),
        ("Contract", "Contract"),
        ("Intern", "Intern"),
        ("Volunteer", "Volunteer"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )

    employee_number = models.CharField(
        max_length=20,
        unique=True
    )

    tsc_number = models.CharField(
        max_length=30,
        unique=True
    )

    national_id = models.CharField(max_length=20)

    phone = models.CharField(max_length=20)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    date_of_birth = models.DateField()

    employment_date = models.DateField()

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True
    )

    qualification = models.CharField(max_length=150)

    specialization = models.CharField(max_length=150)

    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS,
        default="Permanent"
    )

    photo = models.ImageField(
        upload_to="teachers/photos/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class TeacherSubject(models.Model):

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("teacher", "subject")

    def __str__(self):
        return f"{self.teacher} - {self.subject}"

class ClassTeacher(models.Model):

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    stream = models.OneToOneField(
        Stream,
        on_delete=models.CASCADE
    )

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.teacher} - {self.stream}"        