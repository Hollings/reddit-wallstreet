# flask imports
from flask import Flask
from app import app, db, models
from app.models import Trades, Portfolio, Price

# flask scripts imports
from flask_script import Manager
from flask_script import Command
from flask_sqlalchemy import SQLAlchemy

# praw imports
import praw
import re
import requests
import json
import time

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
manager = Manager(app)

class GetNewTrades(Command):
	"prints hello world"

	def isfloat(self, value):
		try:
			float(value)
			return True
		except ValueError:
			return False

	def getStockPrice(self, stock):
		price = models.Price.getPrice(stock);
		return price

	def buyStock(self, symbol, subreddit, permalink):
		# self.portfolio[symbol] += 1
		price = self.getStockPrice(symbol)
		if not price:
			return False
		if not self.isfloat(price):
			price = float(price.replace(",",""))
		with app.app_context():
			Trades.Buy(symbol,price, permalink)
			Portfolio.Buy(symbol, "wallstreetbets")

		# his = models.Trades(symbol=symbol,price=price)
		# db.session.add(his)
		# db.session.commit()
		# self.spent += price
		print("Bought " + symbol + " for " + str(price))

	def sellStock(self, symbol, subreddit, permalink):
		# if self.portfolio[symbol] > 0:
		# 	self.portfolio[symbol] -= 1
		price = self.getStockPrice(symbol)
		if not price:
			return False
		if not self.isfloat(price):
			price = float(price.replace(",",""))
		with app.app_context():
			Trades.Sell(symbol,price, permalink)
			Portfolio.Sell(symbol, "wallstreetbets")
		# 	self.sold += price
		print("Sold " + symbol + " for " + str(price))

	def streamComments(self):
		r = praw.Reddit(client_id='0W5oN1h3MgyxHQ',
					 client_secret=os.environ['CLIENT_SECRET'],
           			 password=os.environ['R_PASSWORD'],
					 user_agent='Wallstreet Bets Checker',
					 username=os.environ['R_USERNAME'])
		i = 0
		subreddit = "wallstreetbets"
		for comment in r.subreddit(subreddit).stream.comments(pause_after=0):
			if comment is None:
				time.sleep(60)
				continue

			i+=1
			results = re.findall(r'(?<![A-Z])[A-Z]{3,5}(?![A-Z])',comment.body)
			for symbol in results[:3]:
				if any(word in comment.body.lower() for word in ['short','sell','bear']):
					self.sellStock(symbol, subreddit, comment.permalink())
				else:
					self.buyStock(symbol, subreddit, comment.permalink())

	def run(self):
		self.streamComments()




if __name__ == "__main__":
	manager.add_command('GetNewTrades', GetNewTrades())
	manager.run()
