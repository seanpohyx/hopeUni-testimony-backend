from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
from sqlalchemy import cast, Date
from database import session, connection
from models import Feeds, Likes, Campus, Lifegroup, Recipient
from datetime import datetime
import time

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@app.route("/", methods=["GET"])
def hello():
	return "hello"

# --------------Feeds API
#get all feeds
@app.route("/api/feeds", methods=["GET"])
@cross_origin()
def getFeeds():
	try:
		feeds = session.query(Feeds,Lifegroup)\
		.filter(Feeds.lg_id == Lifegroup.id)\
		.all()

		results = []
		for f in feeds:
			results.append({
					'id': f[0].id,
					'title': f[0].title,
					'author': f[0].author,
					'message': f[0].message,
					'lg': f[1].lg,
					'datetime': time.strftime('%d-%m-%Y %H:%M', time.localtime(f[0].datetime)),
					'type': f[0].type
				})

		return  jsonify(results)
	except Exception as e:
		return(str(e))

#get the number of feeds for a particular campus
@app.route("/api/feeds_get_count/<int:campus_id>", methods=["GET"])
@cross_origin()
def getFeedsTotal(campus_id):
	try:

		feeds_count = session.query(Feeds,Lifegroup)\
		.filter(Feeds.lg_id == Lifegroup.id)\
		.filter(Lifegroup.campus_id == campus_id)\
		.count()

		return  jsonify({'count': feeds_count})

	except Exception as e:
		return(str(e))

#get all feeds from a particular campus
@app.route("/api/feeds/<int:campus_id>", methods=["GET"])
@cross_origin()
def getFeedsByCampus(campus_id):
	try:

		feeds = session.query(Feeds, Lifegroup, Likes.no_of_likes, Recipient.recipients)\
		.outerjoin(Likes)\
		.outerjoin(Recipient)\
		.filter(Feeds.lg_id == Lifegroup.id)\
		.filter(Lifegroup.campus_id == campus_id)\
		.order_by(Feeds.datetime.desc())\
		.all()

		#isLikeNull = True if feeds[0][2] is None else False

		results = []
		for f in feeds:
			msg = {
				'id': f[0].id,
				'title': f[0].title,
				'author': f[0].author,
				'message': f[0].message,
				'lg': f[1].lg,
				'datetime': time.strftime('%d-%m-%Y %H:%M', time.localtime(f[0].datetime)),
				'type': f[0].type
			}

			if f[2] is not None:
				msg.update( {'no_of_likes' : f[2]} )

			if f[3] is not None:
				msg.update( {'recipients' : f[3]} )

			results.append(msg)

			# if not isLikeNull:
			# 	results.append({
			# 			'id': f[0].id,
			# 			'title': f[0].title,
			# 			'author': f[0].author,
			# 			'message': f[0].message,
			# 			'lg': f[1].lg,
			# 			'datetime': time.strftime('%d-%m-%Y %H:%M', time.localtime(f[0].datetime)),
			# 			'type': f[0].type,
			# 			'no_of_likes': f[2]
			# 		})
			# else:
			# 	results.append({
			# 			'id': f[0].id,
			# 			'title': f[0].title,
			# 			'author': f[0].author,
			# 			'message': f[0].message,
			# 			'lg': f[1].lg,
			# 			'datetime': time.strftime('%d-%m-%Y %H:%M', time.localtime(f[0].datetime)),
			# 			'type': f[0].type
			# 		})

		return  jsonify(results)

	except Exception as e:
		return(str(e))

#set offsets to retrieve feeds for pagination
@app.route("/api/feeds/<int:campus_id>/<int:offset>/<int:limit>", methods=["GET"])
@cross_origin()
def getFeedsByOffsetWith(campus_id, offset, limit):
	try:

		feeds = session.query(Feeds, Lifegroup, Likes.no_of_likes, Recipient.recipients)\
		.outerjoin(Likes)\
		.outerjoin(Recipient)\
		.filter(Feeds.lg_id == Lifegroup.id)\
		.filter(Lifegroup.campus_id == campus_id)\
		.order_by(Feeds.datetime.desc())\
		.offset(offset)\
		.limit(limit)\
		.all()

		#isLikeNull = True if feeds[0][2] is None else False

		results = []
		for f in feeds:
			msg = {
				'id': f[0].id,
				'title': f[0].title,
				'author': f[0].author,
				'message': f[0].message,
				'lg': f[1].lg,
				'datetime': time.strftime('%d-%m-%Y %H:%M', time.localtime(f[0].datetime)),
				'type': f[0].type
			}

			if f[2] is not None:
				msg.update( {'no_of_likes' : f[2]} )

			if f[3] is not None:
				msg.update( {'recipients' : f[3]} )

			results.append(msg)

		return jsonify(results)

	except Exception as e:
		return(str(e))

#post new post into the feeds
@app.route('/api/feeds', methods=['POST'])
@cross_origin()
def create_feeds():

	try:
		if not request.json:
			abort(400)
		else :
			feeds = Feeds( request.json['title'], request.json['author'], request.json['message'], 
				request.json['lg_id'], int(time.time()), request.json['type'])
			session.add(feeds)
			session.commit()

			result = feeds.serialize()

			if 'recipients' in request.json:
				session.refresh(feeds)
				recipient = Recipient( request.json['recipients'], feeds.id)
				session.add(recipient)
				session.commit()
				result.update( {'recipients' : recipient.recipients} )

			if 'no_of_likes' in request.json:
				session.refresh(feeds)
				likes = Likes( feeds.id, request.json['no_of_likes'])
				session.add(likes)
				session.commit()
				result.update( {'no_of_likes' : likes.no_of_likes} )

				# return jsonify({
				# 		"id": feeds.id, 
				# 		"title": feeds.title,
				# 		"author": feeds.author,
				# 		"message": feeds.message,
				# 		"lg_id": feeds.lg_id,
				# 		"datetime": time.strftime('%d-%m-%Y %H:%M', time.localtime(feeds.datetime)),
				# 		"type": feeds.type,
				# 		"no_of_likes": likes.no_of_likes
				# 	})
			
			return jsonify(result)

	except Exception as e:
		return(str(e))

@app.route('/api/feeds/<int:feeds_id>', methods=['PUT'])
@cross_origin()
def update_feeds(feeds_id):

	try:
		result = session.query(Feeds) \
		.filter(Feeds.id == feeds_id) \
		.all()

		if len(result) == 0:
			abort(404)
		# if not request.json:
		# 	abort(400)
		# if 'name' in request.json and type(request.json['name']) is not unicode:
		# 	abort(400)
		# if 'lg' in request.json and type(request.json['lg']) is not unicode:
		# 	abort(400)
		# if 'testimony' in request.json and type(request.json['testimony']) is not unicode:
		# 	abort(400)
		# if 'date' in request.json and type(request.json['date']) is not unicode:
			# abort(400) 

		result[0].title = request.json['title']
		result[0].author = request.json['author']
		result[0].lg_id = request.json['lg_id']
		result[0].message = request.json['message']
		result[0].type = request.json['type']
		session.commit()

		return jsonify([e.serialize() for e in result])

	except Exception as e:
		return(str(e))

#delete any feeds with ID
@app.route('/api/feeds/<int:feeds_id>', methods=['DELETE'])
@cross_origin()
def delete_feeds(feeds_id):
	#cascade delete on: will delete likes too
	try:
		result = session.query(Feeds) \
		.filter(Feeds.id == feeds_id) \
		.delete()

		if result == 0:
			abort(404)
		else:
			session.commit()
			return jsonify({'result': True})

	except Exception as e:
		return(str(e))

#--------------LIKES API
#get likes with feeds ID
@app.route("/api/likes/<int:feeds_id>", methods=["GET"])
@cross_origin()
def getLikes(feeds_id):
	try:
		result = session.query(Likes)\
		.filter(Likes.feeds_id == feeds_id)\
		.all()

		return  jsonify([e.serialize() for e in result])
	except Exception as e:
		return(str(e))

#get likes with feed_id
@app.route('/api/likes', methods=['POST'])
def createLikes():

	try:
		if not request.json:
			abort(400)
		else :
			likes = Likes( request.json['feeds_id'], request.json['no_of_likes'])
			session.add(likes)
			session.commit()
			return jsonify(likes.serialize())

	except Exception as e:
		return(str(e))

#update likes with feed_id
@app.route('/api/likes/<int:feeds_id>/<int:no_of_likes>', methods=['PUT'])
@cross_origin()
def update_likes_with(feeds_id, no_of_likes):

	try:
		result = session.query(Likes) \
		.filter(Likes.feeds_id == feeds_id) \
		.update({Likes.no_of_likes: no_of_likes})

		if result == 0:
			abort(404)

		session.commit()
		return jsonify({'result': True})

	except Exception as e:
		return(str(e))

# #--------------Lg API
@app.route("/api/lifegroup", methods=["GET"])
def getLg():
	try:
		result = session.query(Lifegroup)\
		.all()

		return  jsonify([e.serialize() for e in result])
	except Exception as e:
		return(str(e))

@app.route("/api/lifegroup/<int:campus_id>", methods=["GET"])
@cross_origin()
def getLgWithCampusId(campus_id):
	try:
		result = session.query(Lifegroup)\
		.filter(Lifegroup.campus_id == campus_id)\
		.all()
		
		return  jsonify([e.serialize() for e in result])

	except Exception as e:
		return(str(e))

#--------------Recipient API
#get recipient with feeds ID
@app.route("/api/recipient/<int:feeds_id>", methods=["GET"])
@cross_origin()
def getRecipient(feeds_id):
	try:
		result = session.query(Recipient)\
		.filter(Recipient.feeds_id == feeds_id)\
		.all()

		return  jsonify([e.serialize() for e in result])
	except Exception as e:
		return(str(e))

#get recipient with feed_id
@app.route('/api/recipient', methods=['POST'])
def createRecipients():

	try:
		if not request.json:
			abort(400)
		else :
			recipient = Recipient( request.json['recipients'], request.json['feeds_id'])
			session.add(recipient)
			session.commit()
			return jsonify(recipient.serialize())

	except Exception as e:
		return(str(e))

#update recipient with feed_id
@app.route('/api/recipient/<int:feeds_id>/<string:recipients>', methods=['PUT'])
@cross_origin()
def update_recipients_with(feeds_id, recipients):

	try:
		result = session.query(Recipient) \
		.filter(Recipient.feeds_id == feeds_id) \
		.update({Recipient.recipients: recipients})

		if result == 0:
			abort(404)

		session.commit()
		return jsonify({'result': True})

	except Exception as e:
		return(str(e))



# #--------------Exams API
# @app.route("/api/exams", methods=["GET"])
# @cross_origin()
# def getExams():
# 	try:
# 		exams = session.query(Exams) \
# 		.order_by(Exams.start_time) \
# 		.all()

# 		return  jsonify([e.serialize() for e in exams])

# 	except Exception as e:
# 		return(str(e))

# @app.route('/api/exams/<string:date>', methods=['GET'])
# @cross_origin()
# def getExamsByDate(date):

# 	try:
# 		exams = session.query(Exams) \
# 		.filter(cast(Exams.start_time, Date) == datetime.strptime(date + " 00:00", "%Y-%m-%d %H:%M").date()) \
# 		.order_by(Exams.start_time) \
# 		.all()

# 		if len(exams) == 0:
# 			abort(404)

# 		else:
# 			return jsonify([e.serialize() for e in exams])

# 	except Exception as e:
# 		return(str(e))


# @app.route('/api/exams', methods=['POST'])
# @cross_origin()
# def create_exams():

# 	try:
# 		if not request.json:
# 			abort(400)
# 		else :
# 			exam = Exams( request.json['name'], request.json['lg'],
# 			 request.json['location'], request.json['prayer_warrior'], 
# 			 datetime.strptime(request.json['start_time'], "%Y-%m-%d %H:%M"),
# 			 datetime.strptime(request.json['end_time'], "%Y-%m-%d %H:%M") )
# 			session.add(exam)
# 			session.commit()
# 			return jsonify(exam.serialize())
# 		# return jsonify(database.addTestimony(request.json['lg'],request.json['name'],request.json['testimony']) )
# 	except Exception as e:
# 		return(str(e))


# @app.route('/api/exams/<int:exams_id>', methods=['PUT'])
# @cross_origin()
# def update_exams(exams_id):

# 	try:
# 		result = session.query(Exams) \
# 		.filter(Exams.id == exams_id) \
# 		.all()

# 		if len(result) == 0:
# 			abort(404)
# 		# if not request.json:
# 		# 	abort(400)
# 		# if 'name' in request.json and type(request.json['name']) is not unicode:
# 		# 	abort(400)
# 		# if 'lg' in request.json and type(request.json['lg']) is not unicode:
# 		# 	abort(400)
# 		# if 'testimony' in request.json and type(request.json['testimony']) is not unicode:
# 		# 	abort(400)
# 		# if 'date' in request.json and type(request.json['date']) is not unicode:
# 		# abort(400)

# 		result[0].name = request.json['name']
# 		result[0].lg = request.json['lg']
# 		result[0].location = request.json['location']
# 		result[0].prayer_warrior = request.json['prayer_warrior']
# 		result[0].end_time = datetime.strptime(request.json['end_time'], '%Y-%m-%d %H:%M:%S.%f') 
# 		result[0].start_time = datetime.strptime(request.json['start_time'], '%Y-%m-%d %H:%M:%S.%f') 

# 		session.commit()

# 		return jsonify([e.serialize() for e in result])

# 	except Exception as e:
# 		return(str(e))


# @app.route('/api/exams/<int:exams_id>', methods=['DELETE'])
# @cross_origin()
# def delete_exam(exams_id):

# 	try:
# 		result = session.query(Exams) \
# 		.filter(Exams.id == exams_id) \
# 		.delete() #return 1

# 		if result == 0:
# 			abort(404)
# 		else:
# 			session.commit()
# 			return jsonify({'result': True})

# 	except Exception as e:
# 		return(str(e))




if __name__ == '__main__':
	app.run(debug=True)




