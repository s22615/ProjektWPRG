from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = []
users.append(User(id=1,username='Sebastian',password='123'))


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/home')
def login():
    return render_template('homePage.html')


if __name__ == '__main__':
    app.run()
