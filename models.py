from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import time
Base = declarative_base()

class Campus(Base):

	__tablename__ = 'Campus'

	id = Column(Integer, primary_key=True)
	campus = Column(String)


	def __init__(self, campus):
		self.campus = campus

	def __repr__(self):
		return '<id {}>'.format(self.id)

	def serialize(self):
		return {
			'id': self.id,
			'campus': self.campus
		}

class Lifegroup(Base):

	__tablename__ = 'Lifegroup'

	id = Column(Integer, primary_key=True)
	lg = Column(String)
	campus_id = Column(Integer, ForeignKey('Campus.id'), nullable=False)
	campus = relationship("Campus", foreign_keys='Lifegroup.campus_id')


	def __init__(self, lg, campus_id):
		self.lg = lg
		self.campus_id = campus_id

	def __repr__(self):
		return '<id {}>'.format(self.id)

	def serialize(self):
		return {
		'id': self.id,
		'lg': self.lg,
		'campus_id': self.campus_id
		}

class Likes(Base):

	__tablename__ = 'Likes'

	id = Column(Integer, primary_key=True)
	feeds_id = Column(Integer, ForeignKey("Feeds.id", ondelete='CASCADE'), nullable=False)
	no_of_likes = Column(Integer)
	feeds_table = relationship("Feeds", foreign_keys='Likes.feeds_id')
	feeds = relationship('Feeds', backref=backref('Likes', passive_deletes=True))

	def __init__(self, feeds_id, no_of_likes):
		self.feeds_id = feeds_id
		self.no_of_likes = no_of_likes

	def __repr__(self):
		return '<id {}>'.format(self.id)

	def serialize(self):
		return {
			'id': self.id, 
			'feeds_id': self.feeds_id,
			'no_of_likes': self.no_of_likes
		}

class Feeds(Base):

	__tablename__ = 'Feeds'

	id = Column(Integer, primary_key=True)
	title = Column(String)
	author = Column(String)
	message = Column(String)
	datetime = Column(Integer)
	type = Column(String)
	lg_id = Column(Integer, ForeignKey('Lifegroup.id'), nullable=False)
	lg = relationship("Lifegroup", foreign_keys='Feeds.lg_id')

	def __init__(self, title, author, message, lg_id, datetime, type):
		self.author = author
		self.lg_id = lg_id
		self.message = message
		self.datetime = datetime
		self.type = type
		self.title = title

	def __repr__(self):
		return '<id {}>'.format(self.id)

	def serialize(self):
		return {
			'id': self.id, 
			'title': self.title,
			'author': self.author,
			'message':self.message,
			'lg_id': self.lg.id,
			'datetime': time.strftime('%d-%m-%Y %H:%M', time.localtime(self.datetime)),
			'type': self.type
		}

	def getId(self):
		return self.id

class Recipient(Base):

	__tablename__ = 'Recipient'

	id = Column(Integer, primary_key=True)
	recipients = Column(String)
	feeds_id = Column(Integer, ForeignKey("Feeds.id", ondelete='CASCADE'), nullable=False)
	feeds_table = relationship("Feeds", foreign_keys='Recipient.feeds_id')
	feeds = relationship('Feeds', backref=backref('Recipient', passive_deletes=True))

	def __init__(self, recipients, feeds_id):
		self.recipients = recipients
		self.feeds_id = feeds_id

	def __repr__(self):
		return '<id {}>'.format(self.id)

	def serialize(self):
		return {
			'id': self.id, 
			'recipients': self.recipients,
			'feeds_id': self.feeds_id
		}