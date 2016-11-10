import logging
import os
from flask import Flask, jsonify
from datetime import datetime
import records
from flask import redirect
from flask import request
import validators
from hashids import Hashids
from user_agents import parse

app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'urlShortner.db'),
    HASHSALT='abc123',
    HASHLENGTH='5'
))

def initDB():
    return records.Database('sqlite:////'+app.config['DATABASE'])


def initHashids():
    return Hashids(salt=app.config['HASHSALT'], min_length=app.config['HASHLENGTH'])


def tableCheck():
    # records will create this db on disk if 'urlShortner.db' doesn't exist already
    db = initDB()
    db.query('CREATE TABLE IF NOT EXISTS urls ('
             'id integer primary key autoincrement, '
             'desktop_url text, '
             'desktop_counter int, '
             'mobile_url text, '
             'mobile_counter int, '
             'tablet_url text, '
             'tablet_counter int, '
             'created datetime, '
             'modified datetime)')

def tableEmpty():
    db = initDB()
    db.query('DROP TABLE IF EXISTS urls')
    tableCheck()

def validateRequest(rules):
    desktop_url = request.values.get('desktop_url')
    mobile_url = request.values.get('mobile_url')
    tablet_url = request.values.get('tablet_url')

    if rules != 'update' and (desktop_url is None or desktop_url == ''):
        return jsonify({'message': "parameter desktop_url required"}), 400
    if desktop_url is not None and not validators.url(desktop_url):
        return jsonify({'message': "invalid desktop_url format"}), 400
    if mobile_url is not None and not validators.url(mobile_url):
        return jsonify({'message': "invalid mobile_url format"}), 400
    if tablet_url is not None and not validators.url(tablet_url):
        return jsonify({'message': "invalid tablet_url format"}), 400

    return True

def incrementCounter(row, device):
    db = initDB()
    if row[device+'_counter']:
        counter = row[device+'_counter']+1
    else:
        counter = 1
    db.query('UPDATE urls SET '+device+'_counter=:counter WHERE id=:id', id=row.id, counter=counter)

def displayUrl(row):
    return {
        # 'id': initHashids().encode(row.id),
        'desktop_url':row.desktop_url,
        'desktop_counter':row.desktop_counter,
        'tablet_url':row.tablet_url,
        'tablet_counter': row.tablet_counter,
        'mobile_url':row.mobile_url,
        'mobile_counter': row.mobile_counter,
        'created': timesince(datetime.strptime(row.created, "%Y-%m-%d %H:%M:%S.%f")),
        'modified': timesince(datetime.strptime(row.modified, "%Y-%m-%d %H:%M:%S.%f"))
    }


def timesince(dt, default="just now"):
    now = datetime.now()
    diff = now - dt

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)
    return default


@app.route('/', methods=['GET'])
def getAllUrls():
    db = initDB()
    rows = db.query('select * from urls')
    if len(rows.all()):
        urls = []
        for row in rows:
            urls.append(displayUrl(row))
        return jsonify(urls)
    return jsonify({'message': "no urls found"})


@app.route('/', methods=['POST'])
def createUrl():
    validateResult = validateRequest(rules='create')
    if validateResult != True:
        return validateResult

    db = initDB()
    db.query('INSERT INTO urls (desktop_url, mobile_url, tablet_url, created, modified) VALUES (:desktop_url, :mobile_url, :tablet_url, :created, :modified)',
             desktop_url=request.values.get('desktop_url'),
             mobile_url=request.values.get('mobile_url'),
             tablet_url=request.values.get('tablet_url'),
             created=datetime.now(),
             modified=datetime.now())
    rows = db.query('SELECT MAX(id) as maxid FROM urls');

    hashids = initHashids()
    return jsonify({'short_url':request.url_root+hashids.encode(rows[0]['maxid'])})

@app.route('/<short_url>', methods=['GET'])
def redirectShortUrl(short_url):
    db = initDB()
    hashids = initHashids()
    id = hashids.decode(short_url)
    if id and id[0]:
        rows = db.query('SELECT * FROM urls WHERE id=:id', id=id[0])
        for row in rows:
            user_agent = None
            if request.headers.get('User-Agent') is not None:
                user_agent = parse(request.headers.get('User-Agent'))
            if user_agent is not None and user_agent.is_mobile and row.mobile_url:
                incrementCounter(row, 'mobile')
                return redirect(row.mobile_url)
            elif user_agent is not None and user_agent.is_tablet and row.tablet_url:
                incrementCounter(row, 'tablet')
                return redirect(row.tablet_url)
            else:
                incrementCounter(row,'desktop')
                return redirect(row.desktop_url)
    return jsonify({'message': "invalid short_url"}), 400


@app.route('/<short_url>', methods=['POST'])
def updateUrl(short_url):
    db = initDB()
    hashids = initHashids()
    id = hashids.decode(short_url)

    if id and id[0]:
        validateResult = validateRequest(rules='update')
        if validateResult != True:
            return validateResult

        rows = db.query('SELECT * FROM urls WHERE id=:id', id=id[0])
        for row in rows:
            desktop_url = row.desktop_url
            mobile_url = row.mobile_url
            tablet_url = row.tablet_url
            if request.values.get('desktop_url') is not None:
                desktop_url = request.values.get('desktop_url')
            if request.values.get('mobile_url') is not None:
                mobile_url = request.values.get('mobile_url')
            if request.values.get('tablet_url') is not None:
                tablet_url = request.values.get('tablet_url')

            db.query('UPDATE urls SET desktop_url=:desktop_url, mobile_url=:mobile_url, tablet_url=:tablet_url, modified=:modified WHERE id=:id',
                desktop_url=desktop_url,
                mobile_url=mobile_url,
                tablet_url=tablet_url,
                modified=datetime.now(),
                id=id[0])

            updated_rows = db.query('SELECT * FROM urls WHERE id=:id', id=id[0])
            return jsonify(displayUrl(updated_rows[0]))

    return jsonify({'message': "invalid short_url"}), 400


if __name__ == '__main__':
    # tableDrop()
    tableCheck()
    app.run(debug=True)
