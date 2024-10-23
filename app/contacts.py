from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# Set the secret key to a random value
app.config['SECRET_KEY'] = 'matthews'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'MAtt1233xd'
app.config['MYSQL_DB'] = 'flaskcontact'
app.config['MYSQL_SSL_DISABLED'] = True  # Deshabilitar SSL

mysqldb = MySQL(app)

@app.route('/')
def index():
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    return render_template('index.html', contacts=contacts)

# CRUD de Clientes
@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        try:
            cursor = mysqldb.connection.cursor()
            cursor.execute('INSERT INTO clientes (nombre, email, telefono) VALUES (%s, %s, %s)', (nombre, email, telefono))
            mysqldb.connection.commit()
            flash('Cliente agregado exitosamente!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('index'))

@app.route('/edit_cliente/<id>', methods=['POST', 'GET'])
def get_cliente(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (id,))
    cliente = cursor.fetchall()
    return render_template('edit-cliente.html', cliente=cliente[0])

@app.route('/update_cliente/<id>', methods=['POST'])
def update_cliente(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        try:
            cursor = mysqldb.connection.cursor()
            cursor.execute("""
                UPDATE clientes
                SET nombre = %s,
                    email = %s,
                    telefono = %s
                WHERE id = %s
            """, (nombre, email, telefono, id))
            mysqldb.connection.commit()
            flash('Cliente actualizado exitosamente!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('index'))

@app.route('/delete_cliente/<string:id>')
def delete_cliente(id):
    try:
        cursor = mysqldb.connection.cursor()
        cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Cliente eliminado exitosamente!')
    except Exception as e:
        flash(f'Error: {e}')
    return redirect(url_for('index'))

# CRUD de Reservas
@app.route('/add_reserva', methods=['POST'])
def add_reserva():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        try:
            cursor = mysqldb.connection.cursor()
            cursor.execute('INSERT INTO reservas (cliente_id, fecha_inicio, fecha_fin) VALUES (%s, %s, %s)', (cliente_id, fecha_inicio, fecha_fin))
            reserva_id = cursor.lastrowid
            servicios = request.form.getlist('servicios')
            for servicio in servicios:
                cursor.execute('INSERT INTO detalle_reservas (reserva_id, servicio_id) VALUES (%s, %s)', (reserva_id, servicio))
            mysqldb.connection.commit()
            flash('Reserva agregada exitosamente!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('index'))

@app.route('/edit_reserva/<id>', methods=['POST', 'GET'])
def get_reserva(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM reservas WHERE id = %s', (id,))
    reserva = cursor.fetchall()
    cursor.execute('SELECT * FROM detalle_reservas WHERE reserva_id = %s', (id,))
    detalles = cursor.fetchall()
    return render_template('edit-reserva.html', reserva=reserva[0], detalles=detalles)

@app.route('/update_reserva/<id>', methods=['POST'])
def update_reserva(id):
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        try:
            cursor = mysqldb.connection.cursor()
            cursor.execute("""
                UPDATE reservas
                SET cliente_id = %s,
                    fecha_inicio = %s,
                    fecha_fin = %s
                WHERE id = %s
            """, (cliente_id, fecha_inicio, fecha_fin, id))
            cursor.execute('DELETE FROM detalle_reservas WHERE reserva_id = %s', (id,))
            servicios = request.form.getlist('servicios')
            for servicio in servicios:
                cursor.execute('INSERT INTO detalle_reservas (reserva_id, servicio_id) VALUES (%s, %s)', (id, servicio))
            mysqldb.connection.commit()
            flash('Reserva actualizada exitosamente!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('index'))

@app.route('/delete_reserva/<string:id>')
def delete_reserva(id):
    try:
        cursor = mysqldb.connection.cursor()
        cursor.execute('DELETE FROM reservas WHERE id = %s', (id,))
        cursor.execute('DELETE FROM detalle_reservas WHERE reserva_id = %s', (id,))
        mysqldb.connection.commit()
        flash('Reserva eliminada exitosamente!')
    except Exception as e:
        flash(f'Error: {e}')
    return redirect(url_for('index'))

# CRUD de Habitaciones/Servicios
@app.route('/add_servicio', methods=['POST'])
def add_servicio():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        try:
            cursor = mysqldb.connection.cursor()
            cursor.execute('INSERT INTO servicios (nombre, descripcion, precio) VALUES (%s, %s, %s)', (nombre, descripcion, precio))
            mysqldb.connection.commit()
            flash('Servicio/Habitación agregado exitosamente!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('index'))

@app.route('/edit_servicio/<id>', methods=['POST', 'GET'])
def get_servicio(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM servicios WHERE id = %s', (id,))
    servicio = cursor.fetchall()
    return render_template('edit-servicio.html', servicio=servicio[0])

@app.route('/update_servicio/<id>', methods=['POST'])
def update_servicio(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        try:
            cursor = mysqldb.connection.cursor()
            cursor.execute("""
                UPDATE servicios
                SET nombre = %s,
                    descripcion = %s,
                    precio = %s
                WHERE id = %s
            """, (nombre, descripcion, precio, id))
            mysqldb.connection.commit()
            flash('Servicio/Habitación actualizado exitosamente!')
        except Exception as e:
            flash(f'Error: {e}')
        return redirect(url_for('index'))

@app.route('/delete_servicio/<string:id>')
def delete_servicio(id):
    try:
        cursor = mysqldb.connection.cursor()
        cursor.execute('DELETE FROM servicios WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Servicio/Habitación eliminado exitosamente!')
    except Exception as e:
        flash(f'Error: {e}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
