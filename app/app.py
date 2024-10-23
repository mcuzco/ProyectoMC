from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# Set the secret key to a random value
app.config['SECRET_KEY'] = 'matthews'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Matthews'
app.config['MYSQL_PASSWORD'] = 'MAtt1233xd'
app.config['MYSQL_DB'] = 'flaskcontacts'
app.config['MYSQL_SSL_DISABLED'] = True  # Deshabilitar SSL

mysqldb = MySQL(app)

@app.route('/')
def index():
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    return render_template('index.html', contacts=contacts)

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        cursor = mysqldb.connection.cursor()
        cursor.execute('INSERT INTO contacts (fullname, email, phone) VALUES (%s, %s, %s)', (fullname, email, phone))
        mysqldb.connection.commit()
        flash('Contact added successfully!')
        return redirect(url_for('index'))
    
@app.route('/edit/<id>', methods=['POST', 'GET'])
def get_contact(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (id))
    contact = cursor.fetchall()
    return render_template('edit-contact.html', contact=contact[0])

@app.route('/update/<id>', methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        cursor = mysqldb.connection.cursor()
        cursor.execute("""
            UPDATE contacts
            SET fullname = %s,
                email = %s,
                phone = %s
            WHERE id = %s
        """, (fullname, email, phone, id))
        mysqldb.connection.commit()
        flash('Contact updated successfully!')
        return redirect(url_for('index'))
    
@app.route('/delete/<string:id>')
def delete_contact(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysqldb.connection.commit()
    flash('Contact removed successfully!')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=3000, debug=True)