from flask import Flask, flash, redirect, render_template, request, url_for
from flask_mysqldb import MySQL
app = Flask(__name__)

# Mysql Connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Rafael2002'
app.config['MYSQL_DB'] = 'proyecto'
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
        return redirect(url_for('Index'))

@app.route('/eliminar/<string:id>')
def delete(id):
    cursor3 = mysqldb.connection.cursor()
    cursor3.execute('DELETE FROM TABLE1 WHERE id = {0}'.format(id))
    mysqldb.connection.commit()
    flash('User Deleted')
    return redirect(url_for('Index'))

@app.route('/editar/<string:id>')
def edit(id):
    cursor4 = mysqldb.connection.cursor()
    cursor4.execute('SELECT * FROM TABLE1 WHERE id = {0}'.format(id))
    data1 = cursor4.fetchall()
    return render_template('edit_user.html', useredit = data1)

@app.route('/update/<id>' , methods=['POST'])
def updateInfo(id):
    if request.method == 'POST':
        cursor5 = mysqldb.connection.cursor()

        nuevo_nombres = request.form['new_name']
        nuevo_apellidos = request.form['new_lastname']
        nuevo_edad = request.form['new_age']

        cursor5.execute('UPDATE TABLE1 SET nombres = %s, apellidos = %s, edad = %s WHERE id = %s', (nuevo_nombres,nuevo_apellidos,nuevo_edad, id))
        mysqldb.connection.commit()
        flash('User updated successfully')
        # data1 = cursor5.fetchall()
    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)