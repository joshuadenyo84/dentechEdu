from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django import forms

from .models import Role, User


class RoleAdminForm(forms.ModelForm):
    """Custom model form to expose Group permissions directly inside RoleAdmin."""
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple("Permissions", is_stacked=False),
    )

    class Meta:
        model = Role
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate permissions if editing an existing role
        if self.instance and self.instance.pk and hasattr(self.instance, "group") and self.instance.group:
            self.fields["permissions"].initial = self.instance.group.permissions.all()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    form = RoleAdminForm
    list_display = ("name", "is_staff_role", "dashboard_url", "description")
    search_fields = ("name",)
    exclude = ("group",)

    def save_model(self, request, obj, form, change):
        # 1. Save the Role object (triggers Role.save() which auto-creates obj.group)
        super().save_model(request, obj, form, change)
        
        # 2. Sync permissions to the linked Django Group cleanly
        if "permissions" in form.cleaned_data and obj.group:
            obj.group.permissions.set(form.cleaned_data["permissions"])


# Unregister standard User if already registered by Django Auth to prevent AlreadyRegistered error
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Role & Attributes", {"fields": ("role", "phone", "national_id")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Role & Attributes", {"fields": ("role", "phone", "national_id")}),
    )