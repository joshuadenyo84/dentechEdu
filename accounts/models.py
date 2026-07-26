from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        PRINCIPAL = "PRINCIPAL", "Principal"
        DEPUTY = "DEPUTY", "Deputy Principal"
        TEACHER = "TEACHER", "Teacher"
        PARENT = "PARENT", "Parent"
        STUDENT = "STUDENT", "Student"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"
        LIBRARIAN = "LIBRARIAN", "Librarian"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"

    role = models.CharField(
        max_length=30,
        choices=Roles.choices,
        default=Roles.STUDENT
    )

    phone = models.CharField(max_length=20, blank=True)

    national_id = models.CharField(
        max_length=30,
        blank=True
    )

    profile_photo = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    def save(self, *args, **kwargs):
        # 1. Automatically flag administrative roles so they can pass the admin login page screen
        staff_roles = {self.Roles.ADMIN, self.Roles.PRINCIPAL, self.Roles.DEPUTY, self.Roles.ACCOUNTANT}
        if self.role in staff_roles or self.is_superuser:
            self.is_staff = True
        else:
            self.is_staff = False

        # 2. Save the primary user instance metadata to generating primary key id
        super().save(*args, **kwargs)

        # 3. Automatically link security groups dynamically to avoid script manual setups
        from django.contrib.auth.models import Group
        
        # Clear existing groups first to handle scenarios where a user's role is updated/changed
        self.groups.clear()

        if self.role == self.Roles.ADMIN:
            group = Group.objects.filter(name="School Administrators").first()
            if group:
                self.groups.add(group)
            
        elif self.role in [self.Roles.PRINCIPAL, self.Roles.DEPUTY]:
            group = Group.objects.filter(name="Principals & Deputies").first()
            if group:
                self.groups.add(group)
            
        elif self.role == self.Roles.ACCOUNTANT:
            group = Group.objects.filter(name="Bursars & Accountants").first()
            if group:
                self.groups.add(group)
