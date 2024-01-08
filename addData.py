import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("Project/Face_ID/serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceid-bae32-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "id1":
    {
        "name": "IronMan",
        "major": "Physics",
        "starting_year": 2022,
        "total_attendence": 6,
        "standing": "A",
        "year":4,
        "last_attendence_time": "2023-12-11 00:54:34"
    },
    "id2":
    {
        "name": "Vaibhav Sarswat",
        "major": "CS",
        "starting_year": 2022,
        "total_attendence": 6,
        "standing": "C",
        "year":2,
        "last_attendence_time": "2023-12-11 00:54:34"
    },
    "id3":
    {
        "name": "Elon Musk",
        "major": "Physics",
        "starting_year": 2022,
        "total_attendence": 6,
        "standing": "A",
        "year":3,
        "last_attendence_time": "2023-12-11 00:54:34"
    }
}

for key,value in data.items():
    ref.child(key).set(value)