from flask import Flask, jsonify
import mysql.connector

host = "localhost"
usuario = "root"
contraseña = ""
base_datos_personal = "personal"
base_datos_seguridad = "seguridad"

try:
    conexion_personal = mysql.connector.connect(
        host=host,
        user=usuario,
        password=contraseña,
        database=base_datos_personal
    )
    cursor_personal = conexion_personal.cursor()
except Exception as e:
    print(f"Error en la conexión con 'personal': {e}")

try:
    conexion_seguridad = mysql.connector.connect(
        host=host,
        user=usuario,
        password=contraseña,
        database=base_datos_seguridad
    )
    cursor_seguridad = conexion_seguridad.cursor()
except Exception as e:
    print(f"Error en la conexión con 'seguridad': {e}")

app = Flask(__name__)

@app.route("/rol", methods=["GET"])
def get_rol():
    cursor_personal.execute("SELECT * FROM rol")
    resultados = cursor_personal.fetchall()
    return jsonify(resultados)

