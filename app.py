import cv2
import pytesseract
import mysql.connector
from mysql.connector import Error
from time import strftime
import os

#Cascade classifier for detecting number plate
preTrainedModelPath = os.getcwd()+'/haarcascade_russian_plate_number.xml'
cascodeClassifier = cv2.CascadeClassifier(preTrainedModelPath)

#binding tesseract file path to pytesseract for OCR 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#config freeDB MySQL database 
connection = mysql.connector.connect(host='<host>',
                                     database='<database>',
                                     user='<user>',
                                     password='<password>')
if connection.is_connected():
    db_Info = connection.get_server_info()
    print("Connected to MySQL Server version ", db_Info)
    cursor = connection.cursor()
    cursor.execute("select database();")
    record = cursor.fetchone()
    print("You're connected to database: ", record[0])

#accesing webcam using opencv
rec = cv2.VideoCapture(0)

while(rec.isOpened() and connection.is_connected()):
    ret, frame = rec.read()
    gray = cv2.cvtColor(frame, 0)
    pattern = cascodeClassifier.detectMultiScale(gray,1.1,4)#finding patter inside each frame
    if(len(pattern)>0):
        (x,y,w,h) = pattern[0]
        cropedImage = frame[y:y+h,x:x+w]
        text = pytesseract.image_to_string(cropedImage).strip()#performing OCR
        if(text != ''):
            print(text)
            try:
                sqlQuery = """
                INSERT INTO <table name>
                VALUES
                (DEFAULT,%s, %s)
                """
                data = (strftime("%Y-%M-%d %H:%M:%S"),text)
                cursor.execute(sqlQuery,data)
                connection.commit()
            except:
                connection.rollback()# Rolling back in case of error

        frame = cv2.rectangle(frame,(x, y),(x+w, y+h),(0,255,0),2)#masking
    cv2.imshow('CAMERA', frame)
    if(cv2.waitKey(1)&0XFF == ord('q')):
        break

connection.close()# Closing the connection
rec.release()#Closing web cam
cv2.destroyAllWindows()
