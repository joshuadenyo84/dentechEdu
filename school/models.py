from django.db import models


class School(models.Model):

    name = models.CharField(max_length=200)

    motto = models.CharField(
        max_length=255,
        blank=True
    )

    registration_number = models.CharField(
        max_length=100,
        blank=True
    )

    kra_pin = models.CharField(
        max_length=50,
        blank=True
    )

    phone = models.CharField(max_length=20)

    alternative_phone = models.CharField(
        max_length=20,
        blank=True
    )

    email = models.EmailField()

    website = models.URLField(
        blank=True
    )

    address = models.TextField()

    county = models.CharField(max_length=100)

    sub_county = models.CharField(max_length=100)

    logo = models.ImageField(
        upload_to="school/logo/",
        blank=True,
        null=True
    )

    principal_name = models.CharField(
        max_length=150
    )

    deputy_principal = models.CharField(
        max_length=150,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name