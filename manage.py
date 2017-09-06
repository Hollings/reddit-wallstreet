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
import os

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
manager = Manager(app)

class GetNewTrades(Command):
	def isfloat(self, value):
		# Check if the price value is a float or a string with a comma in it
		try:
			float(value)
			return True
		except ValueError:
			return False

	def getStockPrice(self, stock):
		price = models.Price.getPrice(stock);
		return price

	def buyStock(self, symbol, subreddit, permalink):

		# Get the price value from Google
		price = self.getStockPrice(symbol)

		# If the symbol isn't a real stock, just skip it
		if not price:
			return False

		# Turn a sting with comma into a real float
		if not self.isfloat(price):
			price = float(price.replace(",",""))

		# call the Buy method for the trade history and portfolio models.
		with app.app_context():
			Trades.Buy(symbol,price, permalink)
			Portfolio.Buy(symbol, "wallstreetbets")
		print("Bought " + symbol + " for " + str(price))

	def sellStock(self, symbol, subreddit, permalink):

		# Same as above, but with Sell
		price = self.getStockPrice(symbol)
		if not price:
			return False
		if not self.isfloat(price):
			price = float(price.replace(",",""))
		with app.app_context():
			Trades.Sell(symbol,price, permalink)
			Portfolio.Sell(symbol, "wallstreetbets")
		print("Sold " + symbol + " for " + str(price))

	def streamComments(self):

		r = praw.Reddit(client_id='0W5oN1h3MgyxHQ',
					 client_secret=os.environ['CLIENT_SECRET'],
           			 password=os.environ['R_PASSWORD'],
					 user_agent='Wallstreet Bets Checker',
					 username=os.environ['R_USERNAME'])
		subreddit = "wallstreetbets"

		# Comment stream loops forever, grabbing any new comments on the subreddit.
		# If no new comments are found, wait 1 minute
		for comment in r.subreddit(subreddit).stream.comments(pause_after=0):
			if comment is None:
				time.sleep(60)
				continue

			# If a string of 3 or 4 capital letters are found in the comment
			# body, check if its a 'sell' or 'buy'
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
