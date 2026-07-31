from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Role(models.Model):
    """Dynamic Role model that wraps Django's permission Groups."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # URL name to redirect users upon login (e.g., 'students:dashboard', 'teachers:dashboard')
    dashboard_url = models.CharField(
        max_length=100, 
        default="core:home",
        help_text="URL pattern name for routing user after login."
    )

    # Automatically links this role to Django's built-in Group
    group = models.OneToOneField(
        Group, on_delete=models.CASCADE, related_name="role_profile", null=True, blank=True
    )
    
    is_staff_role = models.BooleanField(
        default=False, 
        help_text="Check if users with this role should access administrative interfaces."
    )

    def save(self, *args, **kwargs):
        # 1. Create linked group if it doesn't exist yet
        if not self.group_id:
            group, _ = Group.objects.get_or_create(name=self.name)
            self.group = group
        else:
            # 2. If role name was edited, sync the underlying Django Group name too
            if self.group.name != self.name:
                self.group.name = self.name
                self.group.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """User model linked dynamically to a Role instance."""
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="users"
    )

    phone = models.CharField(max_length=20, blank=True)
    national_id = models.CharField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        # Handle staff status attribute cleanly before database commit
        if self.role:
            self.is_staff = self.role.is_staff_role or self.is_superuser
        elif not self.is_superuser:
            self.is_staff = False

        super().save(*args, **kwargs)


# =======================================================
# SAFE M2M SYNCING VIA SIGNAL (Executes post-database commit)
# =======================================================

@receiver(post_save, sender=User)
def sync_user_role_to_django_groups(sender, instance, **kwargs):
    """
    Safely synchronizes the custom Role foreign key with Django's native Group M2M 
    field only after the database instance has a fully committed ID.
    """
    if instance.role and instance.role.group:
        instance.groups.set([instance.role.group])
    else:
        instance.groups.clear()