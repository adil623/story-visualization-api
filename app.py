from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask import Response, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from email_validator import validate_email, EmailNotValidError
import datetime

cred = credentials.Certificate("./serviceAccountKey.json")
# Use the application default credentials
firebase_admin.initialize_app(cred, {
    'projectId': 'story-visualization-14b1e',
})

db = firestore.client()

app = Flask(__name__)
api = Api(app)


class RegisterApi(Resource):
    def post(self):
        # get user's registration info (username, email, password)
        # registrationInfo = {
        # fullname: '',
        # email: '',
        # password: '',
        # }
        registrationInfo = request.get_json()

        # Initialize a dictionary for errors
        # errRegistrationInfo = {
        # errFullname: '',
        # errEmail: '',
        # errPassword: ''
        # }

        errRegistrationInfo = {
            "errFullname": '',
            "errEmail": '',
            "errPassword": ''
        }

        # snapshot of user table
        userSnapshot = None
        try:
            # remove all whitespaces from username
            registrationInfo['fullname'] = registrationInfo['fullname'].strip()
            # convert username to lowercase
            registrationInfo['fullname'] = registrationInfo['fullname'].lower()

            # remove all whitespaces from email
            registrationInfo['email'] = registrationInfo['email'].strip()
            # convert email into lowercase
            registrationInfo['email'] = registrationInfo['email'].lower()

            if not registrationInfo['email']:
                errRegistrationInfo['errEmail'] = "Please provide an Email address"
            else:
                try:
                    # Validate.
                    valid = validate_email(registrationInfo['email'])

                    # Update with the normalized form.
                    registrationInfo['email'] = valid.email

                    # Get the usersSnapshot and return the a specific document of a specific id (registrationInfo.email)
                    userSnapshot = db.collection(u'users').document(
                        registrationInfo['email']).get().to_dict()

                    if userSnapshot:
                        errRegistrationInfo['errEmail'] = "Account for this email already exists"

                except EmailNotValidError as e:
                    # email is not valid, exception message is human-readable
                    print(str(e))
                    errRegistrationInfo['errEmail'] = "Email is invalid"
            # Checks if the username is empty
            if not registrationInfo['fullname']:
                errRegistrationInfo['errFullname'] = "Please provide your fullname"
            else:
                # fullname must not constain blank spaces
                if not all(x.isalpha or x == "" for x in registrationInfo['fullname']):
                    errRegistrationInfo['fullname'] = "Please provide a valid username"

            # check the length of password
            if len(registrationInfo['password']) < 5:
                errRegistrationInfo['errPassword'] = "Password must be atleast 5 character long"

            if errRegistrationInfo['errFullname'] != '' or errRegistrationInfo['errEmail'] != '' or errRegistrationInfo['errPassword'] != '':
                return errRegistrationInfo, 400
            else:
                # create the record of new user in database
                db.collection(u'users').document(registrationInfo['email']).set({
                    u"fullname": registrationInfo['fullname'],
                    u"email": registrationInfo['email']
                })
                return {"success": "User Registered"}, 200

        except Exception as e:
            print(e)


class LoginApi(Resource):
    def post(self):
        # get user's login information (email, password)
        # loginInfo = {
        # 'email': '',
        # 'password': ''
        # }

        loginInfo = request.get_json()

        # Initialize a dictionary for errors
        # errLoginInfo = {
        # 'errEmail': '',
        # 'errPassword: ''
        # }

        errLoginInfo = {
            "errEmail": '',
            "errPassword": ''
        }

        # snapshot of user table
        userSnapshot = None

        try:
            # remove all whitespaces from email
            loginInfo['email'] = loginInfo['email'].strip()
            # convert email into lowercase
            loginInfo['email'] = loginInfo['email'].lower()

            if not loginInfo['email']:
                errLoginInfo['errEmail'] = "Please provide an Email address"
            else:
                try:
                    # validate
                    valid = validate_email(loginInfo['email'])

                    # Update with the normalized form.
                    loginInfo['email'] = valid.email

                    # Get the usersSnapshot and return the a specific document of a specific id (loginInfo.email)
                    userSnapshot = db.collection(u'users').document(
                        loginInfo['email']).get().to_dict()

                    if not userSnapshot:
                        errLoginInfo['errEmail'] = "No user exist for this Email address"
                except EmailNotValidError as e:
                    # email is not valid, exception message is human-readable
                    errLoginInfo['errEmail'] = "Email is invalid"

            if len(loginInfo['password']) < 5:
                errLoginInfo['errPassword'] = "Password must be atleast 5 character long"

            if (errLoginInfo['errEmail'] != '') or (errLoginInfo['errPassword'] != ''):
                return errLoginInfo, 400
            else:
                return {"success": "User Logged In"}, 200
        except Exception as e:
            return {'error': f"Error Occurred {e}"}, 400


class ForgetPasswordApi(Resource):
    def post(self):
        # get user's information (email, password)
        # forgetPasswordInfo = {
        # 'email': '',
        # }

        forgetPasswordInfo = request.get_json()

        # Initialize a dictionary for errors
        # errforgetPasswordInfo = {
        # 'errEmail': '',
        # }

        errforgetPasswordInfo = {
            'errEmail': ''
        }

        # snapshot of user table
        userSnapshot = None

        try:
            # remove all whitespaces from email
            forgetPasswordInfo['email'] = forgetPasswordInfo['email'].strip()
            # convert email into lowercase
            forgetPasswordInfo['email'] = forgetPasswordInfo['email'].lower()

            if not forgetPasswordInfo['email']:
                errforgetPasswordInfo['errEmail'] = "Please provide an Email address"
            else:
                try:
                    # validate
                    valid = validate_email(forgetPasswordInfo['email'])

                    # Update with the normalized form.
                    forgetPasswordInfo['email'] = valid.email

                    # Get the usersSnapshot and return the a specific document of a specific id (loginInfo.email)
                    userSnapshot = db.collection(u'users').document(
                        forgetPasswordInfo['email']).get().to_dict()

                    if not userSnapshot:
                        errforgetPasswordInfo['errEmail'] = "No user exist for this Email address"
                except EmailNotValidError as e:
                    # email is not valid, exception message is human-readable
                    errforgetPasswordInfo['errEmail'] = "Email is invalid"

            if errforgetPasswordInfo['errEmail'] != '':
                return errforgetPasswordInfo, 400
            else:
                return {"success": "Email verified"}, 200

        except Exception as e:
            return {'error': f"Error Occurred {e}"}, 400


class SavedSceneApi(Resource):
    def post(self):
        # get scene info (email, password)
        # sceneInfo = {
        # 'text': '',
        # 'email': ''
        # }

        sceneInfo = request.get_json()

        # initialize dictionary to store errors
        # errSceneInfo = {
        # 'errText': '',
        # 'errEmail': ''
        # }

        errSceneInfo = {
            'errText': '',
            'errEmail': ''
        }

        # snapshot of saved scene
        userSnapshot = None

        try:
            # remove all whitespaces from email
            sceneInfo['email'] = sceneInfo['email'].strip()
            # convert email into lowercase
            sceneInfo['email'] = sceneInfo['email'].lower()

            if not sceneInfo['email']:
                errSceneInfo['errEmail'] = "Please provide an Email address"
            else:
                try:
                    # validate
                    valid = validate_email(sceneInfo['email'])

                    # update with normalized form
                    sceneInfo['email'] = valid.email
                    # Get the usersSnapshot and return the a specific document of a specific id (loginInfo.email)
                    userSnapshot = db.collection(u'users').document(
                        sceneInfo['email']).get().to_dict()
                    if not userSnapshot:
                        errSceneInfo['errEmail'] = "No user exist for this Email address"
                except EmailNotValidError as e:
                    errSceneInfo['errEmail'] = "Email is invalid"

            if errSceneInfo['errEmail'] != '':
                return errSceneInfo, 400
            else:
                # get the current date and time of server
                x = datetime.datetime.now()

                # format the date and time as 24/03/2021/17:31:19/Wed
                dataStr = x.strftime("%d") + '/' + x.strftime("%m") + '/' + x.strftime("%Y") + '/' + x.strftime(
                    "%H") + ':' + x.strftime("%M") + ':' + x.strftime("%S") + '/' + x.strftime("%a")

                # add the scene in database
                db.collection(u'saved_scene').add({
                    u"text": sceneInfo['text'],
                    u"email": sceneInfo['email'],
                    u"date": dataStr
                })

                return {"success": "Scene Saved"}, 200

        except Exception as e:
            # email is not valid, exception message is human-readable
            return {'error': f"error occured {e}"}, 400


class ScenesByEmailApi(Resource):
    def get(self, email):
        # remove whitespaces if any
        email = email.strip()
        # convert string to lowercase
        email = email.lower()

        # initialize variable to query firestore
        userSnapshot = None

        if not email:
            return {"failed": "you must provide an Email address"}, 400
        else:
            # validate
            valid = validate_email(email)
            # get the normalize form of email
            email = valid.email

            userSnapshot = db.collection(u'saved_scene').where(
                u'email', u'==', email).order_by(u'date', u'DESCENDING').get()

            if not userSnapshot:
                return {"failed": "No User Found"}, 200
            else:
                # list to store all the retrieved documents
                data = []
                # loop through each document and convert it to dictionary
                for doc in userSnapshot:
                    data.append(doc.to_dict())
                return {"data": data}, 200


class UserByEmailApi(Resource):
    def get(self, email):
        # remove whitespaces if any
        email = email.strip()
        # convert string to lowercase
        email = email.lower()

        # initialize variable to query firestore
        userSnapshot = None
        if not email:
            return {"failed": "you must provide an Email address"}, 400
        else:
            # validate
            valid = validate_email(email)
            # get the normalize form of email
            email = valid.email
            userSnapshot = db.collection(u'users').where(
                u'email', u'==', email).get()
            if not userSnapshot:
                return {"failed": "No User Found"}, 200
            else:
                # list to store all the retrieved documents
                data = []
                # loop through each document and convert it to dictionary
                for doc in userSnapshot:
                    data.append(doc.to_dict())
                return {"user": data}, 200


class RemoveSceneApi(Resource):
    def delete(self, id):
        # remove whitespaces if any
        id = id.strip()
        try:
            # delete user with this id from db
            db.collection(u"saved_scene").document(id).delete()
        except Exception as e:
            return {"error": f"Error Occured {e}"}, 400

        return {"success": "Scene Deleted"}, 200


api.add_resource(RegisterApi, "/api/register")
api.add_resource(LoginApi, "/api/login")
api.add_resource(ForgetPasswordApi, "/api/forget_password")
api.add_resource(SavedSceneApi, "/api/saved_scene", endpoint='scenes')
api.add_resource(ScenesByEmailApi,
                 "/api/saved_scene/get/<string:email>", endpoint="scene")
api.add_resource(UserByEmailApi,
                 "/api/user/get/<string:email>", endpoint="user")
api.add_resource(RemoveSceneApi,
                 "/api/saved_scene/delete/<string:id>")

if __name__ == "__main__":
    app.run(debug=True)
