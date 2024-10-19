from flask import Flask, render_template, request
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mami270802'
app.config['MYSQL_DB'] = 'MCPROJECT'

mysqldb = MySQL(app)

@app.route('/')
def Index():
    return render_template('index.html')


@app.route('/add_record', methods=['POST'])
def add():
    if request.method == 'POST':
        dato1 = request.form['input1']
        cursor =  mysqldb.connection.cursor()
        cursor.execute('')
        return 'recieved'

if __name__ == '__main__':
    app.run(port=3000, debug=True)