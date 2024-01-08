import cv2 as cv
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("Project/Face_ID/serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceid-bae32-default-rtdb.firebaseio.com/",
    'storageBucket':"faceid-bae32.appspot.com"
})



imgList = []
studentIDs = []
path = r'E:\Open CV\Project\Face_ID\Images'
PathList = os.listdir(path)
for i in PathList:
    im =cv.imread(os.path.join(path,i))
    imgList.append(im)
    studentIDs.append(os.path.splitext(i)[0])

    fileName = f'{path}/{i}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

# print (len(imgList))
    
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        cv.cvtColor(img,cv.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding Started ...........")
encodeListKnown = findEncodings(imgList)
encodeListKnownwithIds = [encodeListKnown, studentIDs] 
# print(encodeListKnown)

print("Encoding Complete")

file = open("Project/Face_ID/EncodeFile.p", 'wb')
pickle.dump(encodeListKnownwithIds, file)
file.close()

print("File Saved")