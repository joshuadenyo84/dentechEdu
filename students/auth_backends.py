# students/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from students.models import Student

User = get_user_model()

class StudentAdmissionBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
            
        try:
            # 1. Fetch the student profile using their admission number string
            student = Student.objects.select_related('user').get(admission_number__iexact=username)
            
            # 2. Extract the linked user profile account safely
            user = student.user
            
            # 3. Leverage Django's robust hashing system to verify the password securely
            if user and user.is_active and user.check_password(password):
                return user
                
        except Student.DoesNotExist:
            return None
            
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
