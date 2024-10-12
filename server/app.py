#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate
from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Endpoint to clear the session (reset page views)
@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

# Endpoint to fetch all articles
@app.route('/articles')
def index_articles():
    articles = Article.query.all()
    articles_list = [article.to_dict() for article in articles]
    return jsonify(articles_list), 200

# Paywall feature: Increment page views, limit to 3 articles
@app.route('/articles/<int:id>')
def show_article(id):
    # Initialize page_views if it's the first time
    session['page_views'] = session.get('page_views', 0)

    # Increment page views by 1
    session['page_views'] += 1

    # Check if the user has viewed more than 3 articles
    if session['page_views'] > 3:
        return make_response(
            jsonify({'message': 'Maximum pageview limit reached'}),
            401
        )
    
    # Fetch the article by id
    article = db.session.get(Article, id)
    
    # Return 404 if the article doesn't exist
    if not article:
        return make_response(jsonify({'message': 'Article not found'}), 404)

    # Return the article if within page view limit
    return jsonify(article.to_dict()), 200

if __name__ == '__main__':
    app.run(port=5555)
