import csv
import datetime
import os
import time
from venv import logger
import cv2
from django.shortcuts import render
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from attendance.forms import  StudentForm
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
import mysql.connector







def capture_images(request):
    return render(request, 'capture.html')

def assure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if exists:
        # TrackImages()
        pass
    else:
        print('please contact us')



def insert_register_to_db(student_id, name,serial):
    database = mysql.connector.connect(host='localhost', password='Govi@123', user='root', database='attendance_sheet')
    
    cursor = database.cursor()

    sql = "INSERT INTO intern_project_reg_details (ID, Name,serial) VALUES (%s, %s, %s)"
    check_data = "SELECT * FROM intern_project_reg_details WHERE ID = %s"

    try:
        cursor.execute(check_data, (student_id,))
        result = cursor.fetchone()

        if result:
            # If record exists, do not insert duplicate data
            print("Duplicate record, not inserting.")
            return "Duplicate data, already inserted."
        else:
            # If record does not exist, insert the new record
            cursor.execute(sql, (student_id,name,serial))
            database.commit()
            print("Record inserted successfully.")
            return "Record inserted successfully."
    except mysql.connector.Error as err:
        print("Error:", err)
        database.rollback()
        return f"Error: {err}"
    finally:
        cursor.close()
        database.close()





@csrf_exempt
def register(request):
    message = request.GET.get('message', '') 
    check_haarcascadefile()
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")
    
    serial = 0
    file_path = "StudentDetails/StudentDetails.csv"
    exists = os.path.isfile(file_path)
    
    if exists:
        with open(file_path, 'r') as csvFile:
            reader = csv.reader(csvFile)
            for _ in reader:
                serial += 1
        serial = (serial // 2)
    else:
        with open(file_path, 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(columns)
            serial = 1

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            name = form.cleaned_data['name']

            if name.isalpha() or ' ' in name:
                row = [serial, '', student_id, '', name]
                with open(file_path, 'a+') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(row)

                db_message = insert_register_to_db(student_id,name,serial)
                message = f"Your {student_id} and {name} created successfully, and photo saved! {db_message}"    

                message = f"Your {student_id} and {name} created successfully, and photo saved!"

                return render(request, 'register_page.html', {'form': form, 'message': message})    
            else:
                return JsonResponse({'status': 'error', 'message': 'Enter Correct Name'})
    else:
        form = StudentForm()

    return render(request, 'register_page.html', {'form': form, 'message': message})



def attendance(request):
    return render(request, 'attendance_page.html')






def video_stream():
    cam = cv2.VideoCapture(0)
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)

    while True:
        ret, img = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cam.release()

def video_feed(request):
    return StreamingHttpResponse(video_stream(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')



@csrf_exempt
def capture_image(request):
    if request.method == 'POST':
        try:
            image_data = request.POST.get('image')
            count = request.POST.get('count')
            serial = request.POST.get('serial')
            student_id = request.POST.get('student_id')
            name = request.POST.get('name')

            if image_data and count is not None and serial and student_id and name:
                directory = "TrainingImage/"
                if not os.path.exists(directory):
                    os.makedirs(directory)
                img_data = base64.b64decode(image_data)
                img_name = f"{directory}/{name}.{serial}.{student_id}.{count}.jpg"
                with open(img_name, 'wb') as f:
                    f.write(img_data)

                logger.debug(f"Image saved successfully: {img_name}")
                return JsonResponse({'status': 'success'})
            else:
                logger.error("Missing parameters in the POST request")
                return JsonResponse({'status': 'failure', 'message': 'Missing parameters'})
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return JsonResponse({'status': 'failure', 'message': str(e)})
    else:
        return JsonResponse({'status': 'failure', 'message': 'Invalid request method'})






def track_images(request):
    if request.method == 'GET':
        check_haarcascadefile()

        assure_path_exists("Attendance/")
        assure_path_exists("StudentDetails/")

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        if os.path.isfile("TrainingImageLabel/Trainner.yml"):
            recognizer.read("TrainingImageLabel/Trainner.yml")
        else:
            return JsonResponse({'status': 'failure', 'message': 'Training data missing!'})

        faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX

        if os.path.isfile("StudentDetails/StudentDetails.csv"):
            df = pd.read_csv("StudentDetails/StudentDetails.csv")
        else:
            cam.release()
            cv2.destroyAllWindows()
            return JsonResponse({'status': 'failure', 'message': 'Student details are missing!'})

        attendance_record = set()

        while True:
            ret, im = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
                serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
                if conf < 50:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    name = df.loc[df['SERIAL NO.'] == serial]['NAME'].values
                    student_id = df.loc[df['SERIAL NO.'] == serial]['ID'].values

                    if len(name) > 0 and len(student_id) > 0:
                        name = name[0]
                        student_id = student_id[0]
                        attendance = (str(student_id), '', name, '', date, '', timeStamp)

                        if attendance not in attendance_record:
                            attendance_record.add(attendance)
                            print(f"Recorded: {attendance}")
                        else:
                            print(f"Already recorded: {attendance}")

                        cv2.putText(im, name, (x, y + h + 20), font, 1, (255, 255, 255), 2)
                    else:
                        cv2.putText(im, 'Unknown', (x, y + h + 20), font, 1, (255, 255, 255), 2)
                else:
                    cv2.putText(im, 'Unknown', (x, y + h + 20), font, 1, (255, 255, 255), 2)

            cv2.imshow('Taking Attendance', im)
            if cv2.waitKey(1) == ord('q'):
                break

        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%y-%m-%d')
        attendance_file = f"Attendance/Attendance_{date}.csv"

        if os.path.isfile(attendance_file):
            with open(attendance_file, 'a+', newline='') as csvFile:
                writer = csv.writer(csvFile)
                for attendance in attendance_record:
                    writer.writerow(attendance)
        else:
            with open(attendance_file, 'a+', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(['Id', '', 'Name', '', 'Date', '', 'Time'])
                for attendance in attendance_record:
                    writer.writerow(attendance)

        cam.release()
        cv2.destroyAllWindows()
        return JsonResponse({'status': 'success', 'message': 'Attendance recorded successfully'})

    return render(request, 'attendance_page.html')