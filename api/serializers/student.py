from rest_framework import serializers

from students.models import Student


class StudentSerializer(serializers.ModelSerializer):

    full_name = serializers.ReadOnlyField()

    class Meta:

        model = Student

        fields = "__all__"