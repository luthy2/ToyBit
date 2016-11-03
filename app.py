#ToyBit
#simple clone of bit.ly
#!/env/bin/python
from flask import Flask, jsonify, g, flash, request, render_template, url_for, redirect, session, abort
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL
from flask_sqlalchemy import SQLAlchemy
# from marshmallow import Schema, fields
from datetime import datetime
import requests
import random
import string
import json
from urlparse import urlparse


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SERVER_NAME'] = 'localhost:5000'
app.config['SECRET_KEY'] ='SecretKey'
app.config['DEBUG'] = "True"
db = SQLAlchemy(app)

# ma = Marshmallow(app)

#---------models---------#
class ShortLink(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    original_url = db.Column(db.String())
    unique_id = db.Column(db.String(), index = True)
    timestamp = db.Column(db.DateTime)
    link_visits = db.relationship('Visit', backref='parent', lazy = "dynamic")

    def __init__(self, original_url):
        self.original_url = original_url
        self.unique_id = self.create_unique_id()

    def create_unique_id(self, size=9):
        chars = string.ascii_lowercase + string.digits
        uid = ''.join(random.SystemRandom().choice(chars) for i in xrange(size))
        return uid

    def count_visits(self):
        c = self.link_visits.count()
        return c

    def external_url(self):
        base = app.config["SERVER_NAME"]
        url_as_string = base+'/r/'+str(self.unique_id)
        return url_as_string

    def visits_by_referrer(self):
        v = Visit.query.group_by(Visit.referrer).all()
        return v

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_url = db.Column(db.Integer, db.ForeignKey('short_link.id'))
    referrer = db.Column(db.String())
    timestamp = db.Column(db.DateTime)

    def __init__(self, parent, timestamp):
        self.parent = parent
        self.timestamp = timestamp


# class ShortLinkAPISchema(ma.Schema):
#     class Meta:
#         model=ShortLink



#-----------Forms-----------#
class URLForm(Form):
    url = StringField('url', validators=[DataRequired(), URL(require_tld = False, message = "that doesn't seem like a valid URL. Try adding 'http://'"), Length(min = 7, max = 350)])

#-----------Routes------------#

@app.route("/", methods = ["GET", "POST"])
def index():
    form = URLForm()
    if request.method == "POST":
        if form.validate_on_submit():
            submitted_url = form.url.data
            u = ShortLink.query.filter(ShortLink.original_url.like(submitted_url.lower())).first()
            print submitted_url, u
            if u is None:
                short_link = ShortLink(original_url = submitted_url.lower())
                short_link.timestamp = datetime.utcnow()
                db.session.add(short_link)
                db.session.commit()
                return redirect(url_for("link", unique_id = short_link.unique_id, exists=False))
            else:
                return redirect(url_for("link", unique_id = u.unique_id, exists = True))
        else:
            flash('Hmm Seems like that is not a valid URL. Try adding http://')
            return redirect(url_for("index"))
    return render_template("index.html", form = form)


@app.route('/link/<unique_id>')
def link(unique_id):
    short_link = ShortLink.query.filter_by(unique_id = unique_id).first()
    exists = request.args.get('exists')
    if short_link:
        visits = short_link.visits_by_referrer()
        return render_template("link.html", link = short_link, exists = exists, visits=visits)
    else:
        return abort(404)



@app.route ("/r/<unique_id>")
def shortlink(unique_id):
    s = ShortLink.query.filter_by(unique_id = unique_id).first()
    print s
    if s:
        ref = ''
        if request.referrer:
            parse_obj = urlparse(request.referrer)
            ref = parse_obj.netloc
        v = Visit(parent = s, timestamp = datetime.utcnow())
        v.referrer = ref or None
        db.session.add(v)
        db.session.commit()
        return redirect(s.original_url)
    else:
        return abort(404)

if __name__ == "main":
    app.run()
