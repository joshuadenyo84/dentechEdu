from django.contrib import admin

class TenantBaseAdmin(admin.ModelAdmin):
    """
    Base admin class inherited across apps for multi-database / tenant routing.
    """
    list_per_page = 25
    save_on_top = True
