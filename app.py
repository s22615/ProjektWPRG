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
        session.pop('username', None)
        username = request.form['username']
        password = request.form['password']

        user = query_db("SELECT login,haslo FROM klient WHERE login= ?", (username,))
        if user and user[0]['haslo'] == password:
            session['username'] = user[0]['login']
            session['timestamp'] = datetime.datetime.now()
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        print(request.form)
        loginR = request.form['loginr']
        passR = request.form['passwordr']
        nameR = request.form['name']
        surnameR = request.form['surname']
        peselR = request.form['pesel']
        phoneR = request.form['phone']
        dateR = request.form['date']
        postcodeR = request.form['postcode']
        cityR = request.form['city']
        streetR = request.form['street']

        database = get_db()
        adresIn = database.execute("INSERT INTO adres (kod_pocztowy,miasto,ulica) VALUES (?,?,?)",
                                   (postcodeR, cityR, streetR))
        klientIn = database.execute(
            "INSERT INTO klient (imie,nazwisko,pesel,nr_tel,data_urodzenia,login,haslo,adres) VALUES (?,?,?,?,?,?,?,?)",
            (nameR, surnameR, peselR, phoneR, dateR, loginR, passR, adresIn.lastrowid))
        database.commit()
        adresIn.close()
        klientIn.close()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/createoffer', methods=('GET', 'POST'))
def createoffer():
    username = session['username']
    if request.method == 'POST':
        nrrej = request.form['nrrej']
        marka = request.form['marka']
        model = request.form['model']
        rocznik = request.form['rocznik']
        przebieg = request.form['przebieg']
        pojs = request.form['pojs']
        kolor = request.form['kolor']
        cena = request.form['cena']

        database = get_db()
        selectUser = query_db("SELECT id_klienta FROM klient WHERE login= ?", (username,), True)
        selecteduserId = selectUser['id_klienta']
        samochodIn = database.execute(
            "INSERT INTO samochod (nr_rejestracyjny,marka,model,rocznik,przebieg,pojemnosc_skokowa,kolor,id_wlasciciela) VALUES (?,?,?,?,?,?,?,?)",
            (nrrej, marka, model, rocznik, przebieg, pojs, kolor, selecteduserId))
        selectcarId = query_db("SELECT id_samochodu FROM samochod WHERE nr_rejestracyjny=?", (nrrej,), True)
        selectedcarId = selectcarId['id_samochodu']
        ofertaIn = database.execute("INSERT INTO oferta(cena,id_samochodu) VALUES (?,?)", (cena, selectedcarId))
        database.commit()
        samochodIn.close()
        ofertaIn.close()
        return redirect(url_for('home'))
    return render_template('createoffer.html')


@app.route('/controlsite', methods=('GET', 'POST'))
def controlsite():
    username = session['username']
    database = get_db()
    selectUser = query_db("SELECT id_klienta FROM klient WHERE login= ?", (username,), True)
    selecteduserId = selectUser['id_klienta']
    offer = query_db(
        "SELECT * from oferta inner join samochod s on s.id_samochodu = oferta.id_samochodu join klient k on k.id_klienta = s.id_wlasciciela WHERE id_klienta = ?",
        (selecteduserId,))
    database.commit()
    return render_template('controlSite.html', offer=offer, username=session['username'])


@app.route('/deleteoffer', methods=("POST",))
def deleteoffer():
    id_oferty = request.form['id_oferty']
    print(id_oferty)
    database = get_db()
    deleteselectedOffer = database.execute("DELETE FROM oferta WHERE id_oferty=?", (id_oferty,))
    database.commit()
    deleteselectedOffer.close()
    return redirect(url_for('controlsite'))


@app.route('/editoffer/<int:id_oferty>', methods=("GET", "POST"))
def editoffer(id_oferty):
    if request.method == 'GET':
        offer = query_db(
            "SELECT * from oferta inner join samochod s on s.id_samochodu = oferta.id_samochodu join klient k on k.id_klienta = s.id_wlasciciela WHERE id_oferty=?",
            (id_oferty,))
        return render_template('editOffer.html', each=offer[0])
    elif request.method == 'POST':
        nrrej = request.form['nrrej']
        marka = request.form['marka']
        model = request.form['model']
        rocznik = request.form['rocznik']
        przebieg = request.form['przebieg']
        pojs = request.form['pojs']
        kolor = request.form['kolor']
        cena = request.form['cena']
        id_klienta = request.form['idklienta']
        database = get_db()
        updatecar = database.execute(
            "UPDATE samochod SET nr_rejestracyjny = ?,marka = ?,model = ?,rocznik = ?,przebieg = ?,pojemnosc_skokowa = ?,kolor=? WHERE id_wlasciciela=?",
            (nrrej, marka, model, rocznik, przebieg, pojs, kolor, id_klienta))
        updateoffer = database.execute("UPDATE oferta SET cena=? WHERE id_oferty=?", (cena, id_oferty))
        database.commit()
        updatecar.close()
        updateoffer.close()
        return redirect(url_for('controlsite'))


@app.route('/logout')
def logout():
    del session['username']
    del session['timestamp']
    return redirect(url_for('login'))


@app.route('/home')
def home():
    offer = query_db(
        "SELECT * from oferta inner join samochod s on s.id_samochodu = oferta.id_samochodu join klient k on k.id_klienta = s.id_wlasciciela")
    return render_template('homePage.html', offer=offer, username=session['username'])


@app.route('/home/search', methods=("POST",))
def homesearch():
    modelb = request.form['modelb']
    offer = query_db("""SELECT * FROM samochod 
    JOIN oferta ON samochod.id_samochodu=oferta.id_samochodu 
    JOIN klient ON samochod.id_wlasciciela = klient.id_klienta 
    WHERE model LIKE ?""",("%"+modelb+"%",))
    return render_template('homePage.html', offer=offer, username=session['username'])


if __name__ == '__main__':
    app.run(debug=True)
