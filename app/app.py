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
    
    # Fetch all clients
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    
    # Fetch all reservations with client names and services
    cursor.execute('''
        SELECT reservas.id, clientes.nombre AS cliente_nombre, reservas.fecha_inicio, reservas.fecha_fin
        FROM reservas
        JOIN clientes ON reservas.cliente_id = clientes.id
    ''')
    reservas = cursor.fetchall()
    
    for reserva in reservas:
        cursor.execute('''
            SELECT servicios.nombre
            FROM detalle_reservas
            JOIN servicios ON detalle_reservas.servicio_id = servicios.id
            WHERE detalle_reservas.reserva_id = %s
        ''', (reserva['id'],))
        reserva['servicios'] = cursor.fetchall()
    
    # Fetch all services
    cursor.execute('SELECT * FROM servicios')
    servicios = cursor.fetchall()
    
    return render_template('index.html', clientes=clientes, reservas=reservas, servicios=servicios)

# CRUD de Clientes
@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            telefono = request.form['telefono']
            cursor = mysqldb.connection.cursor()
            cursor.execute('INSERT INTO clientes (nombre, email, telefono) VALUES (%s, %s, %s)', (nombre, email, telefono))
            mysqldb.connection.commit()
            flash('Cliente agregado exitosamente!')
        except Exception as e:
            flash(f'Error al agregar cliente: {str(e)}')
        return redirect(url_for('index'))

@app.route('/edit_cliente/<id>', methods=['POST', 'GET'])
def get_cliente(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (id,))
    cliente = cursor.fetchone()
    return render_template('edit-cliente.html', cliente=cliente)

@app.route('/update_cliente/<id>', methods=['POST'])
def update_cliente(id):
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            telefono = request.form['telefono']
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
            flash(f'Error al actualizar cliente: {str(e)}')
        return redirect(url_for('index'))

@app.route('/delete_cliente/<string:id>', methods=['POST'])
def delete_cliente(id):
    try:
        cursor = mysqldb.connection.cursor()
        # Eliminar reservas asociadas al cliente
        cursor.execute('DELETE FROM detalle_reservas WHERE reserva_id IN (SELECT id FROM reservas WHERE cliente_id = %s)', (id,))
        cursor.execute('DELETE FROM reservas WHERE cliente_id = %s', (id,))
        # Eliminar el cliente
        cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Cliente y sus reservas asociadas eliminados exitosamente!')
    except Exception as e:
        flash(f'Error al eliminar cliente: {str(e)}')
    return redirect(url_for('index'))

# CRUD de Reservas
@app.route('/add_reserva', methods=['POST'])
def add_reserva():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        
        # Verificar que el cliente_id existe en la tabla clientes
        cursor = mysqldb.connection.cursor()
        cursor.execute('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
        cliente = cursor.fetchone()
        
        if cliente:
            cursor.execute('INSERT INTO reservas (cliente_id, fecha_inicio, fecha_fin) VALUES (%s, %s, %s)', (cliente_id, fecha_inicio, fecha_fin))
            reserva_id = cursor.lastrowid
            servicios = request.form.getlist('servicios')
            for servicio_nombre in servicios:
                cursor.execute('SELECT id FROM servicios WHERE nombre = %s', (servicio_nombre,))
                servicio = cursor.fetchone()
                if servicio:
                    cursor.execute('INSERT INTO detalle_reservas (reserva_id, servicio_id) VALUES (%s, %s)', (reserva_id, servicio['id']))
            mysqldb.connection.commit()
            flash('Reserva agregada exitosamente!')
        else:
            flash('Error: Cliente no encontrado.')
        
        return redirect(url_for('index'))

@app.route('/edit_reserva/<id>', methods=['POST', 'GET'])
def get_reserva(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('''
        SELECT reservas.id, reservas.cliente_id, clientes.nombre AS cliente_nombre, reservas.fecha_inicio, reservas.fecha_fin
        FROM reservas
        JOIN clientes ON reservas.cliente_id = clientes.id
        WHERE reservas.id = %s
    ''', (id,))
    reserva = cursor.fetchone()
    
    cursor.execute('SELECT * FROM servicios')
    servicios = cursor.fetchall()
    
    cursor.execute('''
        SELECT servicio_id
        FROM detalle_reservas
        WHERE reserva_id = %s
    ''', (id,))
    detalles = [row['servicio_id'] for row in cursor.fetchall()]
    
    return render_template('edit-reserva.html', reserva=reserva, servicios=servicios, detalles=detalles)

@app.route('/update_reserva/<id>', methods=['POST'])
def update_reserva(id):
    if request.method == 'POST':
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        cursor = mysqldb.connection.cursor()
        cursor.execute("""
            UPDATE reservas
            SET fecha_inicio = %s,
                fecha_fin = %s
            WHERE id = %s
        """, (fecha_inicio, fecha_fin, id))
        cursor.execute('DELETE FROM detalle_reservas WHERE reserva_id = %s', (id,))
        servicios = request.form.getlist('servicios')
        for servicio_nombre in servicios:
            cursor.execute('SELECT id FROM servicios WHERE nombre = %s', (servicio_nombre,))
            servicio = cursor.fetchone()
            if servicio:
                cursor.execute('INSERT INTO detalle_reservas (reserva_id, servicio_id) VALUES (%s, %s)', (id, servicio['id']))
        mysqldb.connection.commit()
        flash('Reserva actualizada exitosamente!')
        return redirect(url_for('index'))

@app.route('/delete_reserva/<string:id>', methods=['POST'])
def delete_reserva(id):
    try:
        cursor = mysqldb.connection.cursor()
        cursor.execute('DELETE FROM detalle_reservas WHERE reserva_id = %s', (id,))
        cursor.execute('DELETE FROM reservas WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Reserva eliminada exitosamente!')
    except Exception as e:
        flash(f'Error al eliminar reserva: {str(e)}')
    return redirect(url_for('index'))

# CRUD de Habitaciones/Servicios
@app.route('/add_servicio', methods=['POST'])
def add_servicio():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        cursor = mysqldb.connection.cursor()
        cursor.execute('INSERT INTO servicios (nombre, descripcion, precio) VALUES (%s, %s, %s)', (nombre, descripcion, precio))
        mysqldb.connection.commit()
        flash('Servicio/Habitación agregado exitosamente!')
        return redirect(url_for('index'))

@app.route('/edit_servicio/<id>', methods=['POST', 'GET'])
def get_servicio(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM servicios WHERE id = %s', (id,))
    servicio = cursor.fetchone()
    return render_template('edit-servicio.html', servicio=servicio)

@app.route('/update_servicio/<id>', methods=['POST'])
def update_servicio(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
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
        return redirect(url_for('index'))

@app.route('/delete_servicio/<string:id>', methods=['POST'])
def delete_servicio(id):
    try:
        cursor = mysqldb.connection.cursor()
        # Eliminar registros asociados en detalle_reservas
        cursor.execute('DELETE FROM detalle_reservas WHERE servicio_id = %s', (id,))
        # Eliminar el servicio
        cursor.execute('DELETE FROM servicios WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Servicio/Habitación eliminado exitosamente!')
    except Exception as e:
        flash(f'Error al eliminar servicio: {str(e)}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)