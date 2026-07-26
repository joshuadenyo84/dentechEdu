from django.db import models
from django.utils import timezone
from academics.models import Grade, Stream


class Student(models.Model):
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

    admission_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )
        
    upi_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True
    )

    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    birth_certificate_number = models.CharField(max_length=30, blank=True)
    
    photo = models.ImageField(
        upload_to="students/photos/",
        blank=True,
        null=True
    )

    grade = models.ForeignKey(Grade, on_delete=models.PROTECT)
    stream = models.ForeignKey(Stream, on_delete=models.PROTECT)
    admission_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["admission_number"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}".replace("  ", " ").strip()

    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"

    def save(self, *args, **kwargs):
        # 1. Automatically generate Admission Number if left blank
        if not self.admission_number:
            current_year = self.admission_date.year if self.admission_date else timezone.now().year
            # Find the last student admitted in the same year to increment the sequence safely
            last_student = Student.objects.filter(admission_number__contains=f"DE/{current_year}/").order_by('-id').first()
            
            if last_student:
                try:
                    last_sequence = int(last_student.admission_number.split('/')[-1])
                    new_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    new_sequence = 1
            else:
                new_sequence = 1
                
            self.admission_number = f"DE/{current_year}/{new_sequence:04d}"

        # Save the student profile record first
        is_new_student = self.pk is None
        super().save(*args, **kwargs)

        # 2. Automated Financial Billing Workflow integration
        if is_new_student:
            from finance.models import FeeStructure, Invoice
            # Lookup active price sheets assigned to this student's specific Grade class
            fee_structures = FeeStructure.objects.filter(grade=self.grade)
            
            for structure in fee_structures:
                # Create an automated financial term invoice row instantly
                Invoice.objects.get_or_create(
                    student=self,
                    term=structure.term,
                    billing_month=self.admission_date,
                    defaults={
                        'total_amount': structure.total_amount,
                        'amount_paid': 0.00,
                        'status': 'UNPAID'
                    }
                )


class Guardian(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="guardians"
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
