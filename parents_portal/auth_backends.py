from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from students.models import Student 

# Dynamically loads your custom 'accounts.User' model safely
User = get_user_model()

class StudentCredentialsBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
            
        try:
            # 1. Fetch student by admission number
            student = Student.objects.get(admission_number=username)
            
            # 2. Check if password matches their UPI number
            if student.upi_number and student.upi_number.strip() == password.strip():
                
                # 3. If no User account is linked yet, create your custom user instance safely
                if not student.user:
                    clean_username = student.admission_number.replace('/', '_').replace('-', '_')
                    
                    user, created = User.objects.get_or_create(
                        username=clean_username,
                        defaults={
                            'first_name': student.first_name,
                            'last_name': student.last_name,
                        }
                    )
                    
                    # Link it back to the student database entry
                    student.user = user
                    student.save()
                
                # Return the authenticated user account back to Django
                return student.user
                
        except ObjectDoesNotExist:
            return None
            
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.objects.DoesNotExist:
            return None
