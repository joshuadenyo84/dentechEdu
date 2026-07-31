from django.db import models
from school.models import School
# ❌ Bad
# from academics.models import Grade
# grade = models.ForeignKey(Grade, on_delete=models.CASCADE)

# ✅ Good
grade = models.ForeignKey('academics.Grade', on_delete=models.CASCADE)
class Notice(models.Model):
    PRIORITY_CHOICES = (
        ("Normal", "Normal"),
        ("Important", "Important"),
        ("Urgent", "Urgent"),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default="Normal")
    
    # Optional target filtering: Leave blank to broadcast to all students
    target_grade = models.ForeignKey('academics.Grade', on_delete=models.SET_NULL, blank=True, null=True, help_text="Leave blank for school-wide notices.")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.priority}] {self.title}"
