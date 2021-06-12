import datetime
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, g


app = Flask(__name__)
app.secret_key = 'wejoaiw29134b21oeaw'

DATABASE = 'C:/Users/Sebastian/PycharmProjects/ProjektWPRG/komisdb.sqlite'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def main():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = query_db("SELECT login,haslo FROM klient WHERE  login= ?", (username,))
        if user and user[0]['haslo'] == password:
            session['username'] = user[0]['login']
            session['timestamp'] = datetime.datetime.now()
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    del session['timestamp']
    return redirect(url_for('login'))


@app.route('/home')
def home():
    # time = (datetime.datetime.now() - session['timestamp'])
    # if time > datetime.timedelta(seconds=30):
    #     return redirect(url_for('logout'))
    return render_template('homePage.html', username=session['username'])


if __name__ == '__main__':
    app.run()
