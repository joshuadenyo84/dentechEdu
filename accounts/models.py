from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    national_id = models.CharField(max_length=30, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    def save(self, *args, **kwargs):
        # 1. Automatically flag administrative roles so they can pass the admin login page screen
        staff_roles = {self.Roles.ADMIN, self.Roles.PRINCIPAL, self.Roles.DEPUTY, self.Roles.ACCOUNTANT}
        if self.role in staff_roles or self.is_superuser:
            self.is_staff = True
        else:
            self.is_staff = False

        # 2. Save primary database metadata
        super().save(*args, **kwargs)


# ==========================================
# AUTOMATED ROLE PERMISSION MAPPING (SIGNALS)
# ==========================================

@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Safely maps the user to their matching school security Group.
    Clears existing mappings if their professional role shifts.
    """
    # Disconnect signal tracking temporarily during execution to prevent recursion loops
    post_save.disconnect(assign_user_to_group, sender=User)

    try:
        # Clear previous groups to handle role re-assignments gracefully
        instance.groups.clear()

        # Define map between roles and group naming conventions
        role_group_map = {
            User.Roles.ADMIN: "School Administrators",
            User.Roles.PRINCIPAL: "Principals & Deputies",
            User.Roles.DEPUTY: "Principals & Deputies",
            User.Roles.ACCOUNTANT: "Bursars & Accountants",
            User.Roles.TEACHER: "Teachers",
            User.Roles.STUDENT: "Students",
            User.Roles.PARENT: "Parents",
            User.Roles.LIBRARIAN: "Librarians",
            User.Roles.RECEPTIONIST: "Receptionists",
        }

        group_name = role_group_map.get(instance.role)

        if group_name:
            # Safely grab or generate the specific security permission block
            group, _ = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)

    finally:
        # Reconnect the signal tracker for subsequent actions
        post_save.connect(assign_user_to_group, sender=User)
