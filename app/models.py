from app import app, db, models
from datetime import datetime, timedelta
import requests
import json

class Trades(db.Model):
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
		his = models.Trades(symbol=symbol,price=price,permalink=permalink,buyOrSell="Bought")
		db.session.add(his)
		db.session.commit()
		print("MODEL BUY")

	@staticmethod
	def Sell(symbol, price, permalink):
		qty = models.Portfolio.query.filter(models.Portfolio.symbol == symbol).filter(models.Portfolio.subreddit == 'wallstreetbets').first()
		if qty is None or int(qty.amount)==0:
			return False
		message = "Sold " + str(qty.amount) + " "
		price = price * qty.amount
		his = models.Trades(symbol=symbol,price=price,permalink=permalink,buyOrSell=message)
		db.session.add(his)
		db.session.commit()
		print("MODEL SELL")

class Subreddit(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	money = db.Column(db.Integer, index=True, unique=False)
	trades = db.relationship('Trades', backref='histories', lazy='dynamic')
	Portfolios = db.relationship('Portfolio', backref='portfolios', lazy='dynamic')
	def __repr__(self):
		return '<Subreddit %r>' % (self.name)

class Portfolio(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(64), index=True, unique=True)
	subreddit = db.Column(db.String(64), db.ForeignKey('subreddit.name'))
	amount = db.Column(db.Integer, index=True, unique=False)
	@staticmethod
	def getTotalValue(subreddit):
		p = models.Portfolio.query.filter(models.Portfolio.subreddit == subreddit)
		totalValue = 0
		for stock in p:
			totalValue += models.Price.getPrice(stock.symbol) * stock.amount
		return totalValue

	@staticmethod
	def Buy(symbol, subreddit):
		p = models.Portfolio.query.filter(models.Portfolio.symbol == symbol).filter(models.Portfolio.subreddit == subreddit).first()
		if p is None:
			p = models.Portfolio(symbol=symbol,subreddit=subreddit, amount = 0)
			
		p.amount += 1
		s = models.Subreddit.query.filter(models.Subreddit.name == subreddit).first()
		s.money -= models.Price.getPrice(symbol)
		db.session.add(p)
		db.session.add(s)

		db.session.commit()

	@staticmethod
	def Sell(symbol, subreddit):
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
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(64), index=True, unique=True)
	price = db.Column(db.Float, index=True, unique=False)
	lastUpdated = db.Column(db.DateTime)

	@staticmethod
	def getPrice(stock):
		price = models.Price.query.filter(models.Price.symbol == stock).first()
		newPrice = False
		if price is None:
			newPrice = True
			price = models.Price(symbol=stock, lastUpdated=datetime.utcnow())
		now = datetime.utcnow()
		priceTime = price.lastUpdated
		if priceTime < datetime.utcnow()-timedelta(seconds=600) or newPrice:
			q = requests.get('http://finance.google.com/finance/info?client=ig&q=' + stock )
			if q.status_code == 200:
				print("------ updating price for " + stock)
				lastPrice = json.loads(q.text[4:])[0]['l']
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