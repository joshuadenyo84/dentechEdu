from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):

    students = serializers.IntegerField()

    teachers = serializers.IntegerField()

    grades = serializers.IntegerField()

    streams = serializers.IntegerField()

    subjects = serializers.IntegerField()