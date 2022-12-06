from flask import Flask
from flask import render_template
from db.DBOperations import getInfo

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html', info = getInfo('''Select id, title from papers order by title'''))

@app.route('/<int:id>')
def showInfo(id):
    return render_template('paper.html', info = getInfo(f'''Select * from papers where id = {id}''')[0])

if __name__ == '__main__':
    app.run()