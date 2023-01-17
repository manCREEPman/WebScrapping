from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./db/data.db'
db = SQLAlchemy(app)

class Papers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text)
    author = db.Column(db.Text)
    annotation = db.Column(db.Text)
    paper_text = db.Column(db.Text)
    url = db.Column(db.Text, unique=True)
    type = db.Column(db.Integer, default=None)

db.create_all()

def getInfo(id=None):
    if id is not None:
        sample = Papers.query.filter_by(id=id).all()
        print(sample)
        return sample
    else:
        return Papers.query.order_by(Papers.title).all()


@app.route('/')
def main():
    info: dict
    try:
        info = getInfo()
    except:
        info = {'error': 'error'}
    return render_template('index.html', info=info)

@app.route('/<int:id>')
def showInfo(id):
    info: dict
    try:
        info = getInfo(id)[0]
    except:
        info = [{'error': 'error'}]
    return render_template('paper.html', info=info)

if __name__ == '__main__':
    app.run()