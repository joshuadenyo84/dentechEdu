from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView

# ✅ Good (Inside function)
def my_student_view(request):
    from timetable.models import TimetableEntry
    # ...

class FinancialInvoiceListView(UserPassesTestMixin, ListView):
    # Your model configurations go here...
    
    def test_func(self):
        """Only lets users belonging to Accountants or Admins view this data."""
        return self.request.user.groups.filter(name__in=['Accountants', 'Admins']).exists()

