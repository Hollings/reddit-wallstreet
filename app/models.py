from app import app, db, models
from datetime import datetime, timedelta
import requests
import json
import time
import csv

class Trades(db.Model):
	# Trades table is a history of all trades.
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(64), index=True, unique=False)
	permalink = db.Column(db.String(1024), index=True, unique=False)
	buyOrSell = db.Column(db.String(64), index=True, unique=False)
	price = db.Column(db.Float, index=True, unique=False)
	timestamp = db.Column(db.DateTime)
	subreddit = db.Column(db.String, db.ForeignKey('subreddit.name'))

	def __repr__(self):
		return '<Trades %r>' % (self.symbol)

	@staticmethod
	def Buy(symbol, price, permalink):

		# Add to the database
		his = models.Trades(symbol=symbol,price=price,permalink=permalink,buyOrSell="Bought",timestamp=datetime.utcnow())
		db.session.add(his)
		db.session.commit()

	@staticmethod
	def Sell(symbol, price, permalink):

		# If there are more than 0 currently in the portfolio, show it as sold
		qty = models.Portfolio.query.filter(models.Portfolio.symbol == symbol).filter(models.Portfolio.subreddit == 'wallstreetbets').first()
		if qty is None or int(qty.amount)==0:
			return False

		# Show how much total money was made in the sell event
		message = "Sold " + str(qty.amount) + " "
		price = price * qty.amount

		# And add it to the database
		his = models.Trades(symbol=symbol,price=price,permalink=permalink,buyOrSell=message,timestamp=datetime.utcnow())
		db.session.add(his)
		db.session.commit()
		print("MODEL SELL")

class Subreddit(db.Model):

	# This is mostly unused. Will be used to track multiple subreddits to see
	# what one invests better. /r/wallstreetbets /r/stocks /r/investing
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	money = db.Column(db.Integer, index=True, unique=False)
	trades = db.relationship('Trades', backref='histories', lazy='dynamic')
	Portfolios = db.relationship('Portfolio', backref='portfolios', lazy='dynamic')
	def __repr__(self):
		return '<Subreddit %r>' % (self.name)

class Portfolio(db.Model):

	# This is a list of currently owned stocks and their quantity
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(64), index=True, unique=True)
	subreddit = db.Column(db.String(64), db.ForeignKey('subreddit.name'))
	amount = db.Column(db.Integer, index=True, unique=False)

	@staticmethod

	def sellAllLowQuantity():
		p = models.Portfolio.query.filter(models.Portfolio.amount <= 2)
		for stock in p:
			models.Portfolio.Sell(stock.symbol, stock.subreddit)

	@staticmethod
	def getTotalValue(subreddit):

		# Add up the total of all owned stocks
		p = models.Portfolio.query.filter(models.Portfolio.subreddit == subreddit)
		totalValue = 0
		for stock in p:
			totalValue += models.Price.getPrice(stock.symbol, False) * stock.amount
		return totalValue

	@staticmethod
	def Buy(symbol, subreddit):

		# If portfolio has none, create it in the database.)
		# If it already exists, just increment it
		p = models.Portfolio.query.filter(models.Portfolio.symbol == symbol).filter(models.Portfolio.subreddit == subreddit).first()
		if p is None:
			p = models.Portfolio(symbol=symbol,subreddit=subreddit, amount = 0)

		# Then, subtract the amount of money spent.
		p.amount += 1
		s = models.Subreddit.query.filter(models.Subreddit.name == subreddit).first()
		s.money -= models.Price.getPrice(symbol)
		db.session.add(p)
		db.session.add(s)
		db.session.commit()

	@staticmethod
	def Sell(symbol, subreddit):

		# Same as above. We sell all of the currently owned stocks instead of
		# just one, to offset the programs bias toward buying.
		p = models.Portfolio.query.filter(models.Portfolio.symbol == symbol).filter(models.Portfolio.subreddit == subreddit).first()
		if p is None or p.amount < 1:
			return False
		s = models.Subreddit.query.filter(models.Subreddit.name == subreddit).first()
		s.money += models.Price.getPrice(symbol) * p.amount
		p.amount = 0
		db.session.add(p)
		db.session.add(s)
		db.session.commit()

class Price(db.Model):

	# We use this table to cache Google Finance prices, so we don't spam the API.
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(64), index=True, unique=True)
	price = db.Column(db.Float, index=True, unique=False)
	lastUpdated = db.Column(db.DateTime)

	@staticmethod
	def getPrice(stock, update = True):

		# Get or create new price
		price = models.Price.query.filter(models.Price.symbol == stock).first()
		newPrice = False
		if price is None:
			newPrice = True
			price = models.Price(symbol=stock, lastUpdated=datetime.utcnow())

		# If this is a new line, or price has not recently been updated, checkZone
		# google's API
		now = datetime.utcnow()
		priceTime = price.lastUpdated
		if (priceTime < datetime.utcnow()-timedelta(seconds=600) or newPrice) and update:
			q = requests.get('http://finance.yahoo.com/d/quotes.csv?s='+ stock + '&f=snl1'  )
			print(q.text)
			if q.status_code == 200:
				# Parse the API response and just pull the stock price.
				lastPrice = q.text.split(',')[-1].strip()
				if lastPrice == "N/A":
					return False
				print("------ updating price for " + stock)
				lastPrice = float(str(lastPrice).replace(",",""))
				price.price = lastPrice
				price.lastUpdated = datetime.utcnow()
				db.session.add(price)
				db.session.commit()

				return lastPrice
			else:
				return False
		else:
			return price.price
