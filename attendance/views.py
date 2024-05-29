import csv
import os
import cv2
from django.shortcuts import redirect, render
from django.http import JsonResponse

from attendance.forms import  StudentForm
from .models import Student, Image
from django.conf import settings

def capture_images(request):
    return render(request, 'capture.html')

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if exists:
        # TrackImages()
        pass
    else:
        print('Error')

def register(request):
    message = ""
    check_haarcascadefile()
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")
    
    serial = 0
    exists = os.path.isfile("StudentDetails/StudentDetails.csv")
    if exists:
        with open("StudentDetails/StudentDetails.csv", 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                serial += 1
        serial = (serial // 2)
    else:
        with open("StudentDetails/StudentDetails.csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
            serial = 1

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            name = form.cleaned_data['name']

            if name.isalpha() or ' ' in name:
                cam = cv2.VideoCapture(0)
                harcascadePath = "haarcascade_frontalface_default.xml"
                detector = cv2.CascadeClassifier(harcascadePath)
                sampleNum = 0

                while True:
                    ret, img = cam.read()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = detector.detectMultiScale(gray, 1.3, 5)
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        sampleNum += 1
                        cv2.imwrite(f"TrainingImage/{name}.{serial}.{student_id}.{sampleNum}.jpg", gray[y:y + h, x:x + w])
                        cv2.imshow('Taking Images', img)

                    if cv2.waitKey(100) & 0xFF == ord('q'):
                        break
                    elif sampleNum > 50:  # Change this to 50 for the requirement
                        break

                cam.release()
                cv2.destroyAllWindows()

                res = f"Images Taken for ID : {student_id}"
                row = [serial, '', student_id, '', name]
                with open('StudentDetails/StudentDetails.csv', 'a+') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(row)

                message = res
            else:
                message = "Enter Correct Name"
    else:
        form = StudentForm()

    return render(request, 'register_page.html', {'form': form, 'message': message})


def attendance(request):
    return render(request, 'attendance_page.html')