from django.contrib import admin
from finance.admin import TenantBaseAdmin  # Inherited for multi-database routing isolation
from .models import Student, Guardian, MedicalRecord, Address


class GuardianInline(admin.TabularInline):
    model = Guardian
    extra = 1
    classes = ("collapse",)  # Keeps it clean; can be expanded when clicked


class MedicalInline(admin.StackedInline):
    model = MedicalRecord
    extra = 0
    can_delete = False  # Protects the health record wrapper from accidental deletion
    verbose_name_plural = "Medical Profile & Special Needs"


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    can_delete = False
    fieldsets = (
        ("Kenyan CBC Administrative Mapping", {
            "fields": ("county", "sub_county", "ward", "village")
        }),
        ("Postal Tracking", {
            "fields": ("postal_address",),
            "classes": ("collapse",)  # Hidden under an accordion block until clicked
        }),
    )


@admin.register(Student)
class StudentAdmin(TenantBaseAdmin):  # Secured via your isolated TenantBaseAdmin routing rules
    list_display = (
        "admission_number",
        "full_name",
        "grade",
        "stream",
        "gender",
        "status",
    )

    search_fields = (
        "admission_number",
        "upi_number",  # Added to allow quick NEMIS lookups
        "first_name",
        "last_name",
    )

    list_filter = (
        "grade",
        "stream",
        "gender",
        "status",
    )

    # Clean layout organization groupings for data entry operators
    fieldsets = (
        ("Core Identity Information", {
            "fields": (("first_name", "middle_name", "last_name"), ("gender", "date_of_birth"), "photo")
        }),
        ("Academic & Government Enrollment Tracking", {
            "fields": (("admission_number", "upi_number"), ("grade", "stream"), ("admission_date", "status"))
        }),
        ("Civil Documentation Registry", {
            "fields": ("birth_certificate_number",),
            "classes": ("collapse",)
        }),
    )

    inlines = [
        GuardianInline,
        MedicalInline,
        AddressInline,
    ]
