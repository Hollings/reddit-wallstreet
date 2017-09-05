from app import app, db, models
from flask import render_template

@app.route('/',  methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	trades = models.Trades.query.all()
	trades.reverse()
	portfolios = models.Portfolio.query.all()
	subreddits = models.Subreddit.query.filter(models.Subreddit.name=='wallstreetbets').first()
	totalValue = models.Portfolio.getTotalValue('wallstreetbets')
	if subreddits:
		netValue = round(subreddits.money + totalValue,2)
	else:
		netValue = 0
	return render_template('index.html',title="12312312#",trades=trades[:20], portfolios=portfolios, subreddits=subreddits, netValue=netValue, spent=round((subreddits.money*-1),2), totalValue=round(totalValue,2))