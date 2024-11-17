from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash  
from flask_mysqldb import MySQL
import os
import MySQLdb
import time


app = Flask(__name__)

# Set the secret key to a random value
app.config['SECRET_KEY'] = 'matthews'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mami270802'
app.config['MYSQL_DB'] = 'flaskcontact3'
app.config['MYSQL_SSL_DISABLED'] = True  # Deshabilitar SSL

mysqldb = MySQL(app)

# URL de Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysqldb.connection.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            # flash('Login exitoso!', 'success')
            return redirect(url_for('home')) 
        else: 
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

# Ruta para Registrase
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']

        if not username or not password:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password) 
        cursor = mysqldb.connection.cursor()

        try:
            cursor.execute('INSERT INTO usuarios (username, password) VALUES (%s, %s)', (username, hashed_password))
            mysqldb.connection.commit()
            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error al registrar usuario: {str(e)}', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    flash('Sesión Cerada', 'info')
    return redirect(url_for('login'))
    
# home
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/clientes')
def clientes():
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    return render_template('clientes/clientes.html',clientes=clientes)
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
        return redirect(url_for('clientes'))
#EDITS CLIENT (GET)
@app.route('/edit_cliente/<id>', methods=['POST', 'GET'])
def get_cliente(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (id,))
    cliente = cursor.fetchone()
    return render_template('clientes/edit-cliente.html', cliente=cliente)
#(POST)
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
        return redirect(url_for('clientes'))

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
    return redirect(url_for('clientes'))

@app.route('/reservas')
def reservas():
    cursor = mysqldb.connection.cursor()
    cursor.execute('''
        SELECT reservas.id, clientes.nombre AS cliente_nombre, habitaciones.numero AS habitacion_numero, reservas.fecha_inicio, reservas.fecha_fin, reservas.estado
        FROM reservas
        JOIN clientes ON reservas.cliente_id = clientes.id
        JOIN habitaciones ON reservas.habitacion_id = habitaciones.id
    ''')
    reservas = cursor.fetchall()
    cursor.execute('SELECT id, nombre FROM servicios')
    servicios = cursor.fetchall()
    cursor.execute('SELECT id, nombre FROM clientes')
    clientes = cursor.fetchall()
    cursor.execute('SELECT id, numero FROM habitaciones WHERE estado = "desocupada"')
    habitaciones = cursor.fetchall()
    
    # Fetch services for each reservation
    for reserva in reservas:
        cursor.execute('''
            SELECT servicios.nombre
            FROM detalle_reservas
            JOIN servicios ON detalle_reservas.servicio_id = servicios.id
            WHERE detalle_reservas.reserva_id = %s
        ''', (reserva['id'],))
        reserva['servicios'] = [row['nombre'] for row in cursor.fetchall()]
    
    return render_template('reservas/reservas.html', servicios=servicios, reservas=reservas, clientes=clientes, habitaciones=habitaciones)

@app.route('/add_reserva', methods=['POST'])
def add_reserva():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        habitacion_id = request.form['habitacion_id']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        servicios = request.form.getlist('servicios')
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                cursor = mysqldb.connection.cursor()
                cursor.execute('SET innodb_lock_wait_timeout = 50')  # Set timeout to 50 seconds
                cursor.execute('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
                cliente = cursor.fetchone()
                if cliente:
                    cursor.execute('INSERT INTO reservas (cliente_id, habitacion_id, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s)', (cliente_id, habitacion_id, fecha_inicio, fecha_fin))
                    reserva_id = cursor.lastrowid
                    cursor.execute("""INSERT INTO facturas (reserva_id, cliente_id, total)
                                        SELECT %s, %s, h.precio
                                        FROM habitaciones h
                                        WHERE h.id = %s""", (reserva_id, cliente_id, habitacion_id))
                    flash('Factura generada')
                    for servicio_id in servicios:
                        cursor.execute('INSERT INTO detalle_reservas (reserva_id, servicio_id, habitacion_id) VALUES (%s, %s, %s)', (reserva_id, servicio_id, habitacion_id))
                    mysqldb.connection.commit()
                    flash('Reserva agregada exitosamente!')
                    
                else:
                    flash('Error: Cliente no encontrado.')
                return redirect(url_for('reservas'))
            except MySQLdb.OperationalError as e:
                if e.args[0] == 1205:  # Lock wait timeout exceeded
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait for 2 seconds before retrying
                        continue
                    else:
                        flash('Error: Lock wait timeout exceeded. Please try again later.')
                else:
                    flash(f'Error: {e}')
    return redirect(url_for('reservas'))

@app.route('/edit_reserva/<id>', methods=['POST', 'GET'])
def get_reserva(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('''
        SELECT reservas.id, reservas.cliente_id, reservas.habitacion_id, clientes.nombre AS cliente_nombre, habitaciones.numero AS habitacion_numero, reservas.fecha_inicio, reservas.fecha_fin, reservas.estado
        FROM reservas
        JOIN clientes ON reservas.cliente_id = clientes.id
        JOIN habitaciones ON reservas.habitacion_id = habitaciones.id
        WHERE reservas.id = %s
    ''', (id,))
    reserva = cursor.fetchone()
    cursor.execute('SELECT id, nombre FROM clientes')
    clientes = cursor.fetchall()
    cursor.execute('SELECT id, numero FROM habitaciones')
    habitaciones = cursor.fetchall()
    cursor.execute('SELECT id, nombre FROM servicios')
    servicios = cursor.fetchall()
    cursor.execute('SELECT servicio_id FROM detalle_reservas WHERE reserva_id = %s', (id,))
    detalles = [row['servicio_id'] for row in cursor.fetchall()]
    return render_template('reservas/edit-reserva.html', reserva=reserva, servicios=servicios, detalles=detalles, clientes=clientes, habitaciones=habitaciones)

@app.route('/update_reserva/<id>', methods=['POST'])
def update_reserva(id):
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        habitacion_id = request.form['habitacion_id']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        estado = request.form['estado']
        cursor = mysqldb.connection.cursor()
        cursor.execute('''
            UPDATE reservas
            SET cliente_id = %s,
                habitacion_id = %s,
                fecha_inicio = %s,
                fecha_fin = %s,
                estado = %s
            WHERE id = %s
        ''', (cliente_id, habitacion_id, fecha_inicio, fecha_fin, estado, id))
        cursor.execute('DELETE FROM detalle_reservas WHERE reserva_id = %s', (id,))
        servicios = request.form.getlist('servicios')
        for servicio_id in servicios:
            cursor.execute('INSERT INTO detalle_reservas (reserva_id, servicio_id, habitacion_id) VALUES (%s, %s, %s)', (id, servicio_id, habitacion_id))
        mysqldb.connection.commit()
        flash('Reserva actualizada exitosamente!')
        return redirect(url_for('reservas'))

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
    return redirect(url_for('reservas'))

@app.route('/servicios')
def servicios():
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM servicios')
    servicios = cursor.fetchall()
    return render_template('servicios/servicios.html', servicios=servicios)

@app.route('/add_servicio', methods=['POST'])
def add_servicio():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        cursor = mysqldb.connection.cursor()
        cursor.execute('INSERT INTO servicios (nombre, descripcion, precio) VALUES (%s, %s, %s)', (nombre, descripcion, precio))
        mysqldb.connection.commit()
        flash('Servicio agregado exitosamente!')
        return redirect(url_for('servicios'))

@app.route('/edit_servicio/<id>', methods=['POST', 'GET'])
def get_servicio(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM servicios WHERE id = %s', (id,))
    servicio = cursor.fetchone()
    return render_template('servicios/edit-servicio.html', servicio=servicio)

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
        flash('Servicio actualizado exitosamente!')
        return redirect(url_for('servicios'))

@app.route('/delete_servicio/<string:id>', methods=['POST'])
def delete_servicio(id):
    try:
        cursor = mysqldb.connection.cursor()
        cursor.execute('DELETE FROM detalle_reservas WHERE servicio_id = %s', (id,))
        cursor.execute('DELETE FROM servicios WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Servicio eliminado exitosamente!')
    except Exception as e:
        flash(f'Error al eliminar servicio: {str(e)}')
    return redirect(url_for('servicios'))

@app.route('/habitaciones') # Ruta para mostrar habitaciones            
def habitaciones():
    cursor = mysqldb.connection.cursor()
    cursor.execute("""SELECT habitaciones.*,
                        sucursales.nombre AS sucursal_nombre
                    FROM habitaciones JOIN sucursales ON habitaciones.sucursal_id = sucursales.id""")
    habitaciones = cursor.fetchall()
    #Fetch all sucursales for the dropdown
    cursor.execute('SELECT id, nombre FROM sucursales')
    sucursales = cursor.fetchall()
    return render_template('habitaciones/habitaciones.html', habitaciones=habitaciones,sucursales = sucursales)

@app.route('/add_habitacion', methods=['POST', 'GET'])
def add_habitacion():
    if request.method == 'POST':
        numero = request.form['numero']
        tipo = request.form['tipo']
        precio = request.form['precio']
        sucursalId = request.form['sucursal_id']
        estado = request.form['estado']
        
        cursor = mysqldb.connection.cursor()
        cursor.execute('SELECT id, nombre FROM sucursales WHERE id = %s', (sucursalId,))
        sucursal = cursor.fetchone()
        if sucursal:
            sucursalId = sucursal['id']
            cursor.execute('INSERT INTO habitaciones (numero, tipo, precio, sucursal_id, estado) VALUES (%s, %s, %s, %s, %s)', (numero, tipo, precio, sucursalId, estado))
            mysqldb.connection.commit()
            flash('Habitación agregada exitosamente!')
        else:
            flash('Sucursal no encontrada.')
        return redirect(url_for('habitaciones'))
    else:
        cursor = mysqldb.connection.cursor()
        cursor.execute('SELECT id, nombre FROM sucursales')
        sucursales = cursor.fetchall()
        return render_template('add-habitacion.html', sucursales=sucursales)
    
@app.route('/edit_habitacion/<id>', methods=['POST', 'GET']) # Ruta para editar habitaciones
def get_habitacion(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM habitaciones WHERE id = %s', (id,))
    habitacion = cursor.fetchone()
    cursor.execute('SELECT id, nombre FROM sucursales')
    sucursales = cursor.fetchall()
    return render_template('habitaciones/edit-habitaciones.html', habitacion=habitacion, sucursales=sucursales)

@app.route('/update_habitacion/<int:id>', methods=['POST'])
def update_habitacion(id):
    if request.method == 'POST':
        numero = request.form['numero']
        tipo = request.form['tipo']
        precio = request.form['precio']
        sucursal_id = request.form['sucursal_id']
        new_state = request.form['estado']
        cursor = mysqldb.connection.cursor()
        cursor.execute("""
            UPDATE habitaciones
            SET numero = %s,
                tipo = %s,
                precio = %s,
                sucursal_id = %s,
                estado = %s
            WHERE id = %s
        """, (numero, tipo, precio, sucursal_id, new_state, id))
        mysqldb.connection.commit()
        flash('Habitación actualizada exitosamente!')
        return redirect(url_for('habitaciones'))
    
@app.route('/delete_habitacion/<string:id>', methods=['POST']) # Ruta para eliminar habitaciones
def delete_habitacion(id):
    try:
        cursor = mysqldb.connection.cursor()
        cursor.execute('DELETE FROM detalle_reservas WHERE habitacion_id = %s', (id,))
        cursor.execute('DELETE FROM habitaciones WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Habitación eliminada exitosamente!')
    except Exception as e:
        flash(f'Error al eliminar habitación: {str(e)}')
    return redirect(url_for('habitaciones'))

@app.route('/sucursales') # Ruta para mostrar sucursales   
def sucursales():
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM sucursales')
    sucursales = cursor.fetchall()
    return render_template('sucursales/sucursales.html', sucursales=sucursales)

@app.route('/add_sucursal', methods=['POST']) # Ruta para agregar sucursales
def add_sucursal():
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        cursor = mysqldb.connection.cursor()
        cursor.execute('INSERT INTO sucursales (nombre, direccion, telefono) VALUES (%s, %s, %s)', (nombre, direccion, telefono))
        mysqldb.connection.commit()
        flash('Sucursal agregada exitosamente!')
        return redirect(url_for('sucursales'))
    
@app.route('/edit_sucursal/<id>', methods=['POST', 'GET']) # Ruta para editar sucursales
def get_sucursal(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM sucursales WHERE id = %s', (id,))
    sucursal = cursor.fetchone()    
    return render_template('sucursales/edit-sucursales.html', sucursal=sucursal)

@app.route('/update_sucursal/<id>', methods=['POST']) # Ruta para actualizar sucursales
def update_sucursal(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        cursor = mysqldb.connection.cursor()
        cursor.execute("""
            UPDATE sucursales
            SET nombre = %s,
                direccion = %s,
                telefono = %s
            WHERE id = %s
        """, (nombre, direccion, telefono, id))
        mysqldb.connection.commit()
        flash('Sucursal actualizada exitosamente!')
        return redirect(url_for('sucursales'))
    
@app.route('/delete_sucursal/<string:id>', methods=['POST']) # Ruta para eliminar sucursales
def delete_sucursal(id):
    try:
        cursor = mysqldb.connection.cursor()
        cursor.execute('DELETE FROM sucursales WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Sucursal eliminada exitosamente!')
    except Exception as e:
        flash(f'Error al eliminar sucursal: {str(e)}')
    return redirect(url_for('sucursales'))

@app.route('/informes') # Ruta para mostrar informes
def informes():
    cursor = mysqldb.connection.cursor()
    cursor.execute('''
        SELECT informes.id, informes.tipo, informes.descripcion, informes.fecha, informes.total, 
               clientes.nombre AS cliente_nombre, reservas.id AS reserva_id, sucursales.nombre AS sucursal_nombre
        FROM informes
        LEFT JOIN clientes ON informes.cliente_id = clientes.id
        LEFT JOIN reservas ON informes.reserva_id = reservas.id
        LEFT JOIN sucursales ON informes.sucursal_id = sucursales.id
    ''')
    informes = cursor.fetchall()
    return render_template('informes/informes.html', informes=informes)


@app.route('/add_informe', methods=['POST', 'GET']) # Ruta para agregar informes   
def add_informe():
    if request.method == 'POST':
        tipo = request.form['tipo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        total = request.form['total']
        cliente_id = request.form['cliente_id']
        reserva_id = request.form['reserva_id']
        sucursal_id = request.form['sucursal_id']
        cursor = mysqldb.connection.cursor()
        cursor.execute('INSERT INTO informes (tipo, descripcion, fecha, total, cliente_id, reserva_id, sucursal_id) VALUES (%s, %s, %s, %s, %s, %s, %s)', (tipo, descripcion, fecha, total, cliente_id, reserva_id, sucursal_id))
        mysqldb.connection.commit()
        flash('Informe agregado exitosamente!')
        return redirect(url_for('informes'))
  


@app.route('/edit_informe/<id>', methods=['POST', 'GET']) # Ruta para editar informes
def get_informe(id):
    cursor = mysqldb.connection.cursor()
    cursor.execute('SELECT * FROM informes WHERE id = %s', (id,))
    informe = cursor.fetchone()
    cursor.execute('SELECT id, nombre FROM clientes')
    clientes = cursor.fetchall()
    cursor.execute('SELECT id FROM reservas')
    reservas = cursor.fetchall()
    cursor.execute('SELECT id, nombre FROM sucursales')
    sucursales = cursor.fetchall()
    return render_template('informes/edit-informe.html', informe=informe, clientes=clientes, reservas=reservas, sucursales=sucursales)

@app.route('/update_informe/<id>', methods=['POST']) # Ruta para actualizar informes
def update_informe(id):
    if request.method == 'POST':
        tipo = request.form['tipo']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']
        total = request.form['total']
        cliente_id = request.form['cliente_id']
        reserva_id = request.form['reserva_id']
        sucursal_id = request.form['sucursal_id']
        cursor = mysqldb.connection.cursor()
        cursor.execute('''
            UPDATE informes
            SET tipo = %s,
                descripcion = %s,
                fecha = %s,
                total = %s,
                cliente_id = %s,
                reserva_id = %s,
                sucursal_id = %s
            WHERE id = %s
        ''', (tipo, descripcion, fecha, total, cliente_id, reserva_id, sucursal_id, id))
        mysqldb.connection.commit()
        flash('Informe actualizado exitosamente!')
        return redirect(url_for('informes'))

@app.route('/delete_informe/<string:id>', methods=['POST']) # Ruta para eliminar informes
def delete_informe(id):
    try:
        cursor = mysqldb.connection.cursor()
        cursor.execute('DELETE FROM informes WHERE id = %s', (id,))
        mysqldb.connection.commit()
        flash('Informe eliminado exitosamente!')
    except Exception as e:
        flash(f'Error al eliminar informe: {str(e)}')
    return redirect(url_for('informes'))

@app.route('/facturas') # Ruta para mostrar facturas
def facturas():
    cursor = mysqldb.connection.cursor()
    cursor.execute('''
        SELECT facturas.id, facturas.fecha_emision, clientes.nombre as clientes 
            FROM facturas 
            JOIN clientes ON facturas.cliente_id = clientes.id
    ''')
    facturas = cursor.fetchall()
    return render_template('facturas/facturas.html', facturas=facturas)
if __name__ == '__main__':
    app.run(debug=True)
