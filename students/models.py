from django.conf import settings
from django.db import models
from django.utils import timezone

from academics.models import Grade, Stream

# ❌ Bad
# from academics.models import Grade
# grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

# ✅ Good
grade = models.ForeignKey('academics.Grade', on_delete=models.CASCADE)
stream = models.ForeignKey('academics.Stream', on_delete=models.CASCADE)
class Student(models.Model):
    # 🔗 Links the real student record to their login account
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="student_record",
    )

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
    STATUS_CHOICES = (
        ("Active", "Active"),
        ("Transferred", "Transferred"),
        ("Graduated", "Graduated"),
        ("Inactive", "Inactive"),
    )

    admission_number = models.CharField(max_length=30, unique=True, blank=True)
    upi_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    birth_certificate_number = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to="students/photos/", blank=True, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT)
    stream = models.ForeignKey(Stream, on_delete=models.PROTECT)
    admission_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["admission_number"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".replace(
            "  ", " "
        ).strip()

    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"

    def save(self, *args, **kwargs):
        # 1. Automatically generate Admission Number if left blank
        if not self.admission_number:
            current_year = (
                self.admission_date.year
                if self.admission_date
                else timezone.now().year
            )
            last_student = (
                Student.objects.filter(
                    admission_number__contains=f"DE/{current_year}/"
                )
                .order_by("-id")
                .first()
            )
            if last_student:
                try:
                    last_sequence = int(
                        last_student.admission_number.split("/")[-1]
                    )
                    new_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    new_sequence = 1
            else:
                new_sequence = 1
            self.admission_number = f"DE/{current_year}/{new_sequence:04d}"

        # Flag if this is a brand new entry before committing to the DB
        is_new_student = self.pk is None

        # Save the student profile record first so we have primary keys available
        super().save(*args, **kwargs)

        # 2. Automated User Account Provisioning
        if not self.user:
            from django.contrib.auth import get_user_model

            User = get_user_model()

            # Generate a clean, lowercase username (e.g., de_2026_0001)
            system_username = self.admission_number.replace("/", "_").lower()

            # Determine the password fallback safely
            if self.upi_number and self.upi_number.strip():
                raw_password = self.upi_number.strip()
            elif (
                self.birth_certificate_number
                and self.birth_certificate_number.strip()
            ):
                raw_password = self.birth_certificate_number.strip()
            else:
                raw_password = "SchoolPassword123"

            # Create user with the correct role assignment
            user_account = User.objects.create_user(
                username=system_username,
                email=f"{system_username}@school.local",
                password=raw_password,
                role="STUDENT",  # Matches User.Roles.STUDENT precisely!
            )

            # Formally link the account back to the student record
            self.user = user_account
            super().save(update_fields=["user"])

        # 3. Automated Financial Billing Workflow
        if is_new_student:
            from finance.models import FeeStructure, Invoice

            fee_structures = FeeStructure.objects.filter(grade=self.grade)
            for structure in fee_structures:
                Invoice.objects.get_or_create(
                    student=self,
                    term=structure.term,
                    billing_month=self.admission_date,
                    defaults={
                        "total_amount": structure.total_amount,
                        "amount_paid": 0.00,
                        "status": "UNPAID",
                    },
                )


class Guardian(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="guardians"
    )
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"


class MedicalRecord(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    disability = models.TextField(blank=True)
    special_needs = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)

    def __str__(self):
        return self.student.full_name


class Address(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    village = models.CharField(max_length=100, blank=True)
    postal_address = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.student.full_name