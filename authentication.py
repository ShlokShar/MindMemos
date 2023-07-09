import pyrebase

config = {
    'apiKey': "AIzaSyD9XUOf2mSEAzA89mVOOG3sObE7mUu3TkU",
    'authDomain': "mindmemos-87cef.firebaseapp.com",
    'projectId': "mindmemos-87cef",
    'storageBucket': "mindmemos-87cef.appspot.com",
    'messagingSenderId': "201688760625",
    'appId': "1:201688760625:web:43084e8c80569b991f3010",
    'databaseURL' : ""
}

firebase = pyrebase.initialize_app(config)
authentication = firebase.auth()