import cv2 as cv
import os
import pickle
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("Project/Face_ID/serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceid-bae32-default-rtdb.firebaseio.com/",
    'storageBucket':"faceid-bae32.appspot.com"
})

modeType = 0
counter = 0
id = -1
bucket = storage.bucket()
imgStudent = []

cap = cv.VideoCapture(0) 

cap.set(3, 640)
cap.set(4, 480)

imgBack = cv.imread('E:\Open CV\Project\Face_ID\Resources\img.png')

imgModeList = []
path = r'E:\Open CV\Project\Face_ID\Resources\Modes'
for i in range(1,5) :
    im =cv.imread(os.path.join(path,f'im{i}.png'))
    imgModeList.append(im)
# print (len(imgModeList))


# Load the encoding file

print("Loading Encode File ....")
file = open('Project/Face_ID/EncodeFile.p', 'rb')
encodeListKnownwithIds = pickle.load(file)

encodeListKnown, studentIDs = encodeListKnownwithIds
# print(studentIDs)
print ("Encode File Loaded")


while True:
    isTrue, img= cap.read()

    imgS = cv.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv.cvtColor(imgS,cv.COLOR_BGR2RGB)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    faceCurrFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

    #Detecting the face
    haar_cascade = cv.CascadeClassifier("E:\Open CV\Project\Face_ID\haar_face.xml")
    
    imgBack[44:44+633, 808:808+414] = imgModeList[modeType]

    if faceCurrFrame:
        for encodeFace,faceloc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                face_rect = haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
                
                id = studentIDs[matchIndex]
                if counter == 0:
                    counter = 1
                    modeType = 1
                    cv.putText(imgBack,"Loading ......", (162,55+320), cv.FONT_HERSHEY_COMPLEX, 2, (0,255,0), 3)
                    cv.imshow('Attendence', imgBack)
                    cv.waitKey(1)
                    # if cv.waitKey(1) & 0xFF==ord('d'):
                    #     break
                
                for (x,y,w,h) in face_rect:
                    cv.rectangle(img, (x,y), (x+w,y+h), (0,255,0), thickness = 2)

    imgBack[162:162+480,55:55+640] = img

    
    if counter !=0:

        if counter == 1:
            #Get the Data
            studentInfo = db.reference(f'Students/{id}').get()
            print(studentInfo)

            #Get the Storage
            blob = bucket.get_blob(f'E:\Open CV\Project\Face_ID\Images/{id}.png')
            # array = np.frombuffer(blob.download_as_string(), np.uint8)
            if blob is not None and blob.exists():
                array = np.frombuffer(blob.download_as_string(), np.uint8)
            else:
                print("Blob is None. Check your code for proper initialization.")

            imgStudent = cv.imdecode(array, cv.COLOR_BGRA2BGR)
            imgStudent = cv.resize(imgStudent, (216,216), interpolation=cv.INTER_CUBIC)

            # Update the data
            datetimeObject = datetime.strptime(studentInfo['last_attendence_time'], "%Y-%m-%d %H:%M:%S")

            secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
            print(secondsElapsed)
            if secondsElapsed > 30:
                ref = db.reference(f'Students/{id}')
                studentInfo['total_attendence'] += 1
                ref.child('total_attendence').set(studentInfo['total_attendence'])
                ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            else:
                modeType = 3
                counter = 0
                imgBack[44:44+633, 808:808+414] = imgModeList[modeType]


        if 10<counter<20:
            modeType=2
            imgBack[44:44+633, 808:808+414] = imgModeList[modeType]

        if modeType!=3:

            if counter<=10:
                cv.putText(imgBack, str(studentInfo['total_attendence']), (861,125), cv.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1)
                cv.putText(imgBack, str(studentInfo['major']), (1006,550), cv.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 1)
                cv.putText(imgBack, str(id), (1006,493), cv.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 1)
                cv.putText(imgBack, str(studentInfo['standing']), (910,625), cv.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                cv.putText(imgBack, str(studentInfo['year']), (1025,625), cv.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                cv.putText(imgBack, str(studentInfo['starting_year']), (1125,625), cv.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
                    
                (w, h), _ = cv.getTextSize(studentInfo['name'], cv.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (414 - w)//2
                cv.putText(imgBack, str(studentInfo['name']), (808 + offset,445), cv.FONT_HERSHEY_COMPLEX, 1, (50,50,50), 1)
                
                imgBack[175:175+216,909:909+216] = imgStudent

        counter += 1

        if counter>=20:
            counter = 0
            modeType = 0
            imgStudent = []
            studentInfo = []
            imgBack[44:44+633, 808:808+414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0


    cv.imshow('Attendence', imgBack)

    if cv.waitKey(2) & 0xFF==ord('d'):
        break

cap.release()
cv.destroyAllWindows()