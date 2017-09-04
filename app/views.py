from app import app, db, models
from flask import render_template

@app.route('/')
@app.route('/index')

def index():
	trades = models.Trades.query.all()
	trades.reverse()
	portfolios = models.Portfolio.query.all()
	subreddits = models.Subreddit.query.filter(models.Subreddit.name=='wallstreetbets').first()
	totalValue = models.Portfolio.getTotalValue('wallstreetbets')
	netValue = subreddits.money + totalValue
	return render_template('index.html',title="12312312#",trades=trades, portfolios=portfolios, subreddits=subreddits, netValue=netValue)