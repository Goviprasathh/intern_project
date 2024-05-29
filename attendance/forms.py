from django import forms

class StudentForm(forms.Form):
    student_id = forms.CharField(label='Student ID', max_length=100)
    name = forms.CharField(label='Name', max_length=100)
