from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Student


@receiver(pre_save, sender=Student)
def generate_admission_number(sender, instance, **kwargs):

    if instance.admission_number:
        return

    last_student = Student.objects.order_by("id").last()

    if last_student:
        next_id = last_student.id + 1
    else:
        next_id = 1

    instance.admission_number = f"ADM{next_id:05d}"