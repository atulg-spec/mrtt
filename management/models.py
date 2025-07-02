from django.db import models

class JobOpening(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=50)
    description = models.TextField()
    requirements = models.TextField()

    def __str__(self):
        return self.title
