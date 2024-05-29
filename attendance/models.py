from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

class Image(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='TrainingImage/')
    created_at = models.DateTimeField(auto_now_add=True)
