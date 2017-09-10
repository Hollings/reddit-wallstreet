from app import app, db, models
from flask import render_template

@app.route('/',  methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])

def index():
	trades = models.Trades.query.order_by(models.Trades.timestamp.desc())
	portfolios = models.Portfolio.query.filter(models.Portfolio.amount > 0).order_by(models.Portfolio.amount.desc())
	subreddits = models.Subreddit.query.filter(models.Subreddit.name=='wallstreetbets').first()
	totalValue = models.Portfolio.getTotalValue('wallstreetbets')
	if subreddits and totalValue:
		netValue = round(subreddits.money + totalValue,2)
	else:
		netValue = 0
	return render_template('index.html',title="WallStreetBets",trades=trades[:40], portfolios=portfolios, subreddits=subreddits, netValue=netValue, spent=round((subreddits.money*-1),2), totalValue=round(totalValue,2))