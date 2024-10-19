from flask import Flask, flash, redirect, render_template, request, url_for
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mami270802'
app.config['MYSQL_DB'] = 'MCPROJECT'

mysqldb = MySQL(app)

#setting
app.secret_key='mysecretkey'

@app.route('/')
def Index():
    cursor2 = mysqldb.connection.cursor()
    cursor2.execute('SELECT * FROM TABLE1')
    data = cursor2.fetchall()
    return render_template('index.html', users = data)


@app.route('/add_record', methods=['POST'])
def add():
    if request.method == 'POST':
        names = request.form['nombres']
        lastnames = request.form['apellidos']
        ages = request.form['edad']
        cursor =  mysqldb.connection.cursor()
        cursor.execute('INSERT INTO TABLE1 (nombres,apellidos,edad) VALUES (%s,%s,%s)',(names,lastnames,ages))
        mysqldb.connection.commit()
        flash('User added Succesfully')
        return redirect(url_for('index.html'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)