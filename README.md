### Installation

```bash
git clone https://github.com/mcuzco/ProyectoMC
cd PROYECTOMC
pip install -r requirements.txt
python app/main.py
```
### Database
```bash
# Crear la base de datos usando el script Flask_DB.sql
# Asegúrate de tener instalado MySQL en tu ordenador

# Abre MySQL desde la línea de comandos
mysql -u root -p

# Crea una nueva base de datos
CREATE DATABASE ProyectoMC;

# Sal del cliente MySQL
exit

# Importa el script Flask_DB.sql en la nueva base de datos
mysql -u root -p ProyectoMC < PROYECTOMC/sql/Flask_DB.sql
```


### Configuración de `app.py`

Abre el archivo `app.py` y reemplaza la siguiente sección con la información correspondiente a tu ordenador:

```python
# Set the secret key to a random value
app.config['SECRET_KEY'] = '<key>'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '<your password>'
app.config['MYSQL_DB'] = 'ProyectoMC'
app.config['MYSQL_SSL_DISABLED'] = True  # Deshabilitar SSL
```

Asegúrate de reemplazar `<key>` con una clave secreta aleatoria y `<your password>` con la contraseña de tu usuario de MySQL.

```

