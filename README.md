# ToyBit
A toy [bit.ly](http://www.bitly.com) clone

## features
#### link shortening
a simple flask app with one feature. takes a url and converts into a shortened link.
any visit to the shortened link will redirect to the original url

#### not much else
pretty basic stuff. link shortening and basic metrics on shortened links.

## installing
You will want to set up in a [virtualenv](https://virtualenv.pypa.io/en/stable/)
```
$ virtualenv env
$ source env/bin/activate
```

install the requirements
```
$ python setup.py
```

set the environment variables and run the dev server
```
$ export FLASK_APP=app.py
$ flask run
* Serving Flask app "app"
* Running on http://127.0.0.1:5000/
```

## improvements

#### project structure
The project isn't very well structured. The main app.py module should be broken up into seperate modules.

#### tests
There are no tests

#### performance
bit.ly is processing somewhere north of [2500 redirect](http://highscalability.com/blog/2014/7/14/bitly-lessons-learned-building-a-distributed-system-that-han.html) requests per second. Scalability would clearly be an issue for this tiny app. An easy improvement to make would be to cache every url according to its ```unique_id```. Even the smallest/cheapest AWS ElastiCache instance could hold ~700k unique urls. Another  would be to perform all analytics operations asynchronously.

#### front End improvements
bit.ly website has a nice AJAX link look up feature which displays the shortened link without triggering a page reload. An easy implementation of this feature would be to convert the ```/link/<unique_id>``` route into an api endpoint.

#### others
user accounts
more analytics with nice charts
