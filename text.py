import flask
from flask import Flask,jsonify,request
from flask_restful import Api,Resource
from pymongo import MongoClient
import bcrypt
import spacy

app=Flask(__name__)
api=Api(app)

client=MongoClient("mongodb://localhost:27017")
db=client.SimilarityDB
users=db["Users"]


def UserExist(username):
	if users.find({"Username":username}).count()==0:
		return False
	else:
		return True

class Register(Resource):
	def post(self):
		postedData = request.get_json()
		username=postedData["username"]
		password=postedData["password"]

		if UserExist(username):
			retJson={
				"status":"Invalid Username",
				"msg" : "Invalid Username"

			}
			return jsonify(retJson)

		hashed_pw=bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())
		users.insert({
			"Username":username,
			"Password" : hashed_pw,
			"Tokens" : 6
			})

		retJson={
			"status":200,
			"msg"   : "You'vs Succesfully signed up"
					}

		return jsonify(retJson)

def verifyPw(username,password):
	if not UserExist(username):
		return False

	hashed_pw=users.find({"Username":username})[0]["Password"]
	if bcrypt.hashpw(password.encode('utf8'),hashed_pw)==hashed_pw:
		return True
	else:
		return False

def countToken(username):
	countToken=users.find({"Username":username})[0]["Tokens"]
	return countToken
	pass

class Detect(Resource):
	def post(self):
		postedData=request.get_json()
		username=postedData["username"]
		password=postedData["password"]

		text1=postedData["text1"]
		text2=postedData["text2"]

		if not UserExist(username):
			retJson={
				"status":"301",
				"msg": "Invalid Username"	
					}
			return jsonify(retJson)

		correct_pw=verifyPw(username,password)

		if not correct_pw:
			retJson={
				"status": "302",
				"msg": "Invalid Password"
			}
			return jsonify(retJson)

		num_token=countToken(username)



		if num_token<=0:
			retJson={
			"status": 302,
			"msg" : "Sorry You are Out Of Token"
			}

			return jsonify(retJson)

		nlp=spacy.load('en_core_web_sm')
		text1=nlp(text1)
		text2=nlp(text2)

		ratio=text1.similarity(text2)

		retJson={
			"status":200,
			"similarity": ratio,
			"Msg": "Simialrity Score Calculated Succesfully"
			}

		current_token=countToken(username)
		users.update({
			"Username": username,

			},{"$set":{"Tokens": current_token-1}})

		return jsonify(retJson)

class Refil(Resource):
	def post(self):
		postedData=request.get_json()
		username=postedData["username"]
		password=postedData["password"]
		refil_amount=postedData["refil"]

		if not UserExist(username):
			retJson={
				"status":301,
				"msg": "Invalid Username"
			}
			return jsonify(retJson)

		current_token=countToken(username)
		users.update({"Username":username},{"$set":{"Tokens":refil_amount+current_token}})
		retJson={
		"status":200,
		"msg":"Refil Succesfully"
		}

		return jsonify(retJson)

api.add_resource(Register,'/register')
api.add_resource(Detect,'/detect')
api.add_resource(Refil,'/refil')

if __name__=="main":
	app.run(debug=True)







