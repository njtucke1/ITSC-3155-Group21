import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date

cred = credentials.Certificate('./ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()
today = str(date.today().strftime('%m-%d-%y'))
doc_ref = db.collection('COVID-19-Data').document(today)
doc_ref.set({
    'name': 'yaw',
    'class': 'ITCS 3155',
})

try:
    doc = doc_ref.get()
    print('Document data: {}'.format(doc.to_dict()))
except:
    print('No such document!')