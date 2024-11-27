from flask import Flask, jsonify, request, send_file, render_template
import mysql.connector
import bcrypt


app = Flask(__name__)
from flask_cors import CORS

# Esto habilitará CORS para todas las rutas
CORS(app)


def get_connection(database_name):
    return mysql.connector.connect(
        host='20.151.93.235',
        user='uvp',
        password='rojito33',
        database=database_name
    )

base_datos_personal = 'personal'
base_datos_seguridad = 'seguridad'

@app.get('/api/rol')
def get_roles():
    cursor = None ##############
    conn = None
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rol")
        roles = cursor.fetchall()
        return jsonify(roles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@app.post('/api/rol')
def create_rol():
    descripcion = request.json.get('descripcion')
    estatus = request.json.get('estatus')
    
    if not descripcion or not estatus:
        return jsonify({"error": "Los campos 'descripcion' y 'estatus' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_rol FROM rol WHERE id_rol LIKE 'R%' ORDER BY id_rol DESC LIMIT 1")
        last_id = cursor.fetchone()
        
        if last_id:
            last_num = int(last_id[0][1:])
            nuevo_id = f"R{last_num + 1:03d}"
        else:
            nuevo_id = "R001"
        cursor.execute(
            "INSERT INTO rol (id_rol, descripcion, estatus) VALUES (%s, %s, %s)",
            (nuevo_id, descripcion, estatus)
        )
        conn.commit()
        return jsonify({"message": "Rol creado exitosamente", "id_rol": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.delete('/api/rol/<string:id_rol>')
def delete_rol(id_rol):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rol WHERE id_rol = %s", (id_rol,))
        conn.commit()
        return jsonify({"message": "Rol eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/rol/<string:id_rol>')
def update_rol(id_rol):
    descripcion = request.json.get('descripcion')
    estatus = request.json.get('estatus')
    if not descripcion or not estatus:
        return jsonify({"error": "Los campos 'descripcion' y 'estatus' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE rol SET descripcion = %s, estatus = %s WHERE id_rol = %s",
            (descripcion, estatus, id_rol)
        )
        conn.commit()
        return jsonify({"message": "Rol actualizado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.get('/api/rol/<string:id_rol>')
def get_rol(id_rol):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rol WHERE id_rol = %s", (id_rol,))
        rol = cursor.fetchone()
        if rol:
            return jsonify(rol)
        return jsonify({"error": "Rol no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

##################################
@app.get('/api/empleado')
def get_empleados():
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)

        # Consulta para obtener todos los datos de empleado junto con la descripción del rol
        cursor.execute("""
            SELECT 
                empleado.id_empleado,
                empleado.nombre,
                empleado.direccion,
                empleado.telefono,
                empleado.correo,
                empleado.fecha_ingreso,
                empleado.id_rol,
                empleado.estatus,
                empleado.fecha_modificacion,
                rol.descripcion AS rol_descripcion
            FROM 
                empleado
            LEFT JOIN 
                rol ON empleado.id_rol = rol.id_rol
        """)
        
        empleados = cursor.fetchall()
        return jsonify(empleados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/empleado')
def create_empleado():
    nombre = request.json.get('nombre')
    direccion = request.json.get('direccion')
    telefono = request.json.get('telefono')
    correo = request.json.get('correo')
    fecha_ingreso = request.json.get('fecha_ingreso')
    id_rol = request.json.get('id_rol')
    estatus = request.json.get('estatus', 'activo')
    
    if not all([nombre, direccion, telefono, correo, fecha_ingreso, id_rol]):
        return jsonify({"error": "Todos los campos son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_empleado FROM empleado WHERE id_empleado LIKE 'E%' ORDER BY id_empleado DESC LIMIT 1")
        last_id = cursor.fetchone()
        if last_id:
            last_num = int(last_id[0][1:])
            nuevo_id = f"E{last_num + 1:03d}"
        else:
            nuevo_id = "E001"
        cursor.execute(
            """
            INSERT INTO empleado 
            (id_empleado, nombre, direccion, telefono, correo, fecha_ingreso, id_rol, estatus) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (nuevo_id, nombre, direccion, telefono, correo, fecha_ingreso, id_rol, estatus)
        )
        conn.commit()
        return jsonify({"message": "Empleado creado exitosamente", "id_empleado": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/empleado/<string:id_empleado>')
def update_empleado(id_empleado):
    nombre = request.json.get('nombre')
    direccion = request.json.get('direccion')
    telefono = request.json.get('telefono')
    correo = request.json.get('correo')
    fecha_ingreso = request.json.get('fecha_ingreso')
    id_rol = request.json.get('id_rol')
    estatus = request.json.get('estatus', 'activo')
    if not all([nombre, direccion, telefono, correo, fecha_ingreso, id_rol]):
        return jsonify({"error": "Todos los campos 'nombre', 'direccion', 'telefono', 'correo', 'fecha_ingreso' e 'id_rol' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE empleado 
            SET nombre = %s, direccion = %s, telefono = %s, correo = %s, fecha_ingreso = %s, id_rol = %s, estatus = %s 
            WHERE id_empleado = %s
            """,
            (nombre, direccion, telefono, correo, fecha_ingreso, id_rol, estatus, id_empleado)
        )
        conn.commit()
        return jsonify({"message": "Empleado actualizado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.delete('/api/empleado/<string:id_empleado>')
def delete_empleado(id_empleado):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empleado WHERE id_empleado = %s", (id_empleado,))
        conn.commit()
        return jsonify({"message": "Empleado eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#########################################
@app.get('/api/asistencia')
def get_asistencias():
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT asistencia.id_asistencia, asistencia.id_empleado, asistencia.fecha_ingreso, 
                   asistencia.hora_entrada, asistencia.hora_salida, asistencia.estatus, 
                   asistencia.fecha_modificacion, empleado.nombre AS empleado_nombre 
            FROM asistencia 
            LEFT JOIN empleado ON asistencia.id_empleado = empleado.id_empleado
        """)
        asistencias = cursor.fetchall()
        
        # Convertir las horas de TIME a formato string (HH:MM:SS)
        for asistencia in asistencias:
            if asistencia['hora_entrada']:
                asistencia['hora_entrada'] = str(asistencia['hora_entrada'])
            if asistencia['hora_salida']:
                asistencia['hora_salida'] = str(asistencia['hora_salida'])
        
        return jsonify(asistencias)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/asistencia')
def create_asistencia():
    id_empleado = request.json.get('id_empleado')
    fecha_ingreso = request.json.get('fecha_ingreso')
    hora_entrada = request.json.get('hora_entrada')
    hora_salida = request.json.get('hora_salida')
    estatus = request.json.get('estatus', 'activo')
    if not all([id_empleado, fecha_ingreso, estatus]):
        return jsonify({"error": "Los campos 'id_empleado', 'fecha_ingreso' y 'estatus' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_asistencia FROM asistencia WHERE id_asistencia LIKE 'A%' ORDER BY id_asistencia DESC LIMIT 1")
        last_id = cursor.fetchone()
        if last_id:
            last_num = int(last_id[0][1:])
            nuevo_id = f"A{last_num + 1:03d}"
        else:
            nuevo_id = "A001"
        if hora_entrada:
            hora_entrada = str(hora_entrada)
        if hora_salida:
            hora_salida = str(hora_salida)
        cursor.execute(
            """
            INSERT INTO asistencia 
            (id_asistencia, id_empleado, fecha_ingreso, hora_entrada, hora_salida, estatus) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nuevo_id, id_empleado, fecha_ingreso, hora_entrada, hora_salida, estatus)
        )
        conn.commit()
        return jsonify({"message": "Asistencia creada exitosamente", "id_asistencia": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/asistencia/<string:id_asistencia>')
def update_asistencia(id_asistencia):
    id_empleado = request.json.get('id_empleado')
    fecha_ingreso = request.json.get('fecha_ingreso')
    hora_entrada = request.json.get('hora_entrada')
    estatus = request.json.get('estatus', 'activo')
    
    if not id_empleado or not fecha_ingreso or not hora_entrada or not estatus:
        return jsonify({"error": "Los campos 'id_empleado', 'fecha_ingreso', 'hora_entrada' e 'estatus' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE asistencia SET id_empleado = %s, fecha_ingreso = %s, hora_entrada = %s, estatus = %s WHERE id_asistencia = %s",
            (id_empleado, fecha_ingreso, hora_entrada, estatus, id_asistencia)
        )
        conn.commit()
        return jsonify({"message": "Asistencia actualizado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.delete('/api/asistencia/<string:id_asistencia>')
def delete_asistencia(id_asistencia):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM asistencia WHERE id_asistencia = %s", (id_asistencia,))
        conn.commit()
        return jsonify({"message": "Asistencia eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
#######################################
@app.get('/api/seguridad_personal')
def get_seguridad_personal():
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT seguridad_personal.*, empleado.nombre AS empleado_nombre, rol.descripcion AS rol_descripcion 
            FROM seguridad_personal 
            LEFT JOIN empleado ON seguridad_personal.id_empleado = empleado.id_empleado 
            LEFT JOIN rol ON seguridad_personal.id_rol = rol.id_rol
        """)
        seguridad_personal = cursor.fetchall()
        return jsonify(seguridad_personal)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/seguridad_personal')
def create_seguridad_personal():
    usuario = request.json.get('usuario')
    contrasena = request.json.get('contrasena')
    id_empleado = request.json.get('id_empleado')
    id_rol = request.json.get('id_rol')
    estatus = request.json.get('estatus', 'activo')
    if not all([usuario, contrasena, id_empleado]):
        return jsonify({"error": "Los campos 'usuario', 'contrasena' e 'id_empleado' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario FROM seguridad_personal WHERE id_usuario LIKE 'S%' ORDER BY id_usuario DESC LIMIT 1")
        last_id = cursor.fetchone()
        if last_id:
            last_num = int(last_id[0][1:])
            nuevo_id = f"S{last_num + 1:03d}"
        else:
            nuevo_id = "S001"
        cursor.execute("""
            INSERT INTO seguridad_personal 
            (id_usuario, usuario, contrasena, id_empleado, id_rol, estatus) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nuevo_id, usuario, contrasena, id_empleado, id_rol, estatus))
        conn.commit()
        return jsonify({"message": "Usuario de seguridad creado exitosamente", "id_usuario": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.put('/api/seguridad_personal/<string:id_usuario>')
def update_seguridad_personal(id_usuario):
    usuario = request.json.get('usuario')
    contrasena = request.json.get('contrasena')
    id_empleado = request.json.get('id_empleado')
    id_rol = request.json.get('id_rol')
    estatus = request.json.get('estatus', 'activo')
    
    if not usuario or not contrasena or not id_empleado or not id_rol or not estatus:
        return jsonify({"error": "Los campos 'usuario', 'contrasena', 'id_empleado', 'id_rol' e 'estatus' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE seguridad_personal SET usuario = %s, contrasena = %s, id_empleado = %s, id_rol = %s, estatus = %s WHERE id_usuario = %s",
            (usuario, contrasena, id_empleado, id_rol, estatus, id_usuario)
        )
        conn.commit()
        return jsonify({"message": "Usuario actualizado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.delete('/api/seguridad_personal/<string:id_usuario>')
def delete_seguridad_personal(id_usuario):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM seguridad_personal WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        return jsonify({"message": "Usuario eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

###############################
@app.get('/api/evaluacion')
def get_evaluaciones():
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT evaluacion.id_evaluacion, evaluacion.id_empleado, evaluacion.fecha, 
                   evaluacion.puntuacion, evaluacion.comentarios, evaluacion.estatus, 
                   evaluacion.fecha_modificacion, 
                   empleado.nombre AS empleado_nombre
            FROM evaluacion 
            LEFT JOIN empleado ON evaluacion.id_empleado = empleado.id_empleado
        """)
        evaluaciones = cursor.fetchall()
        return jsonify(evaluaciones)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/evaluacion')
def create_evaluacion():
    id_empleado = request.json.get('id_empleado')
    fecha = request.json.get('fecha')
    puntuacion = request.json.get('puntuacion')
    comentarios = request.json.get('comentarios')
    estatus = request.json.get('estatus', 'activo')
    if not id_empleado or not fecha or not puntuacion:
        return jsonify({"error": "Los campos 'id_empleado', 'fecha' y 'puntuacion' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_evaluacion FROM evaluacion WHERE id_evaluacion LIKE 'EV%' ORDER BY id_evaluacion DESC LIMIT 1")
        last_id = cursor.fetchone()
        if last_id:
            last_num = int(last_id[0][2:])
            nuevo_id = f"EV{last_num + 1:03d}"
        else:
            nuevo_id = "EV001"
        cursor.execute(
            """
            INSERT INTO evaluacion 
            (id_evaluacion, id_empleado, fecha, puntuacion, comentarios, estatus) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nuevo_id, id_empleado, fecha, puntuacion, comentarios, estatus)
        )
        conn.commit()
        return jsonify({"message": "Evaluación creada exitosamente", "id_evaluacion": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/evaluacion/<string:id_evaluacion>')
def update_evaluacion(id_evaluacion):
    id_empleado = request.json.get('id_empleado')
    fecha = request.json.get('fecha')
    puntuacion = request.json.get('puntuacion')
    comentarios = request.json.get('comentarios', '')
    estatus = request.json.get('estatus', 'activo')
    if not id_empleado or not fecha or not puntuacion:
        return jsonify({"error": "Los campos 'id_empleado', 'fecha' y 'puntuacion' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE evaluacion 
            SET id_empleado = %s, fecha = %s, puntuacion = %s, comentarios = %s, estatus = %s
            WHERE id_evaluacion = %s
            """,
            (id_empleado, fecha, puntuacion, comentarios, estatus, id_evaluacion)
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Evaluación no encontrada"}), 404
        return jsonify({"message": "Evaluación actualizada exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.delete('/api/evaluacion/<string:id_evaluacion>')
def delete_evaluacion(id_evaluacion):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evaluacion WHERE id_evaluacion = %s", (id_evaluacion,))
        conn.commit()
        return jsonify({"message": "Evaluacion eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

################################
@app.get('/api/nomina')
def get_nominas():
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT nomina.*, 
                   empleado.nombre AS empleado_nombre
            FROM nomina 
            LEFT JOIN empleado ON nomina.id_empleado = empleado.id_empleado
        """)
        nominas = cursor.fetchall()
        return jsonify(nominas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/nomina')
def create_nomina():
    id_empleado = request.json.get('id_empleado')
    periodo = request.json.get('periodo')
    salario = request.json.get('salario')
    estatus = request.json.get('estatus', 'activo')
    if not id_empleado or not periodo or not salario:
        return jsonify({"error": "Los campos 'id_empleado', 'periodo' y 'salario' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_nomina FROM nomina WHERE id_nomina LIKE 'N%' ORDER BY id_nomina DESC LIMIT 1")
        last_id = cursor.fetchone()
        if last_id:
            last_num = int(last_id[0][1:])
            nuevo_id = f"N{last_num + 1:03d}"
        else:
            nuevo_id = "N001"
        cursor.execute(
            """
            INSERT INTO nomina (id_nomina, id_empleado, periodo, salario, estatus) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nuevo_id, id_empleado, periodo, salario, estatus)
        )
        conn.commit()
        return jsonify({"message": "Nómina creada exitosamente", "id_nomina": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/nomina/<string:id_nomina>')
def update_nomina(id_nomina):
    id_empleado = request.json.get('id_empleado')
    periodo = request.json.get('periodo')
    salario = request.json.get('salario')
    estatus = request.json.get('estatus', 'activo')
    if not id_empleado or not periodo or not salario:
        return jsonify({"error": "Los campos 'id_empleado', 'periodo' y 'salario' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nomina WHERE id_nomina = %s", (id_nomina,))
        existing_nomina = cursor.fetchone()
        if not existing_nomina:
            return jsonify({"error": "Nómina no encontrada"}), 404
        cursor.execute(
            """
            UPDATE nomina 
            SET id_empleado = %s, periodo = %s, salario = %s, estatus = %s 
            WHERE id_nomina = %s
            """,
            (id_empleado, periodo, salario, estatus, id_nomina)
        )
        conn.commit()
        return jsonify({"message": "Nómina actualizada exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.delete('/api/nomina/<string:id_nomina>')
def delete_nomina(id_nomina):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM nomina WHERE id_nomina = %s", (id_nomina,))
        conn.commit()
        return jsonify({"message": "Nomina eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

###################################################
@app.get('/api/horario')
def get_horarios():
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT horario.*, empleado.nombre AS empleado_nombre
            FROM horario 
            LEFT JOIN empleado ON horario.id_empleado = empleado.id_empleado
        """)
        horarios = cursor.fetchall()
        for horario in horarios:
            if horario['hora_entrada']:
                horario['hora_entrada'] = str(horario['hora_entrada'])
            if horario['hora_salida']:
                horario['hora_salida'] = str(horario['hora_salida'])
        return jsonify(horarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/horario')
def create_horario():
    try:
        id_empleado = request.json.get('id_empleado')
        fecha = request.json.get('fecha')
        hora_entrada = request.json.get('hora_entrada')
        hora_salida = request.json.get('hora_salida')
        estatus = request.json.get('estatus', 'activo')
        if not id_empleado or not fecha or not hora_entrada or not hora_salida or not estatus:
            return jsonify({"error": "Los campos 'id_empleado', 'fecha', 'hora_entrada', 'hora_salida' y 'estatus' son requeridos"}), 400
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_horario FROM horario WHERE id_horario LIKE 'H%' ORDER BY id_horario DESC LIMIT 1")
        last_id = cursor.fetchone()
        if last_id:
            last_num = int(last_id[0][1:])
            nuevo_id = f"H{last_num + 1:03d}"
        else:
            nuevo_id = "H001"
        cursor.execute("""
            INSERT INTO horario (id_horario, id_empleado, fecha, hora_entrada, hora_salida, estatus)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nuevo_id, id_empleado, fecha, hora_entrada, hora_salida, estatus))
        conn.commit()
        return jsonify({"message": "Horario creado exitosamente", "id_horario": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/horario/<string:id_horario>')
def update_horario(id_horario):
    try:
        id_empleado = request.json.get('id_empleado')
        fecha = request.json.get('fecha')
        hora_entrada = request.json.get('hora_entrada')
        hora_salida = request.json.get('hora_salida')
        estatus = request.json.get('estatus')
        if not id_empleado or not fecha or not hora_entrada or not hora_salida or estatus is None:
            return jsonify({"error": "Los campos 'id_empleado', 'fecha', 'hora_entrada', 'hora_salida' y 'estatus' son requeridos"}), 400
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_horario FROM horario WHERE id_horario = %s", (id_horario,))
        existing_horario = cursor.fetchone()
        if not existing_horario:
            return jsonify({"error": "Horario no encontrado"}), 404
        cursor.execute("""
            UPDATE horario 
            SET id_empleado = %s, fecha = %s, hora_entrada = %s, hora_salida = %s, estatus = %s
            WHERE id_horario = %s
        """, (id_empleado, fecha, hora_entrada, hora_salida, estatus, id_horario))
        conn.commit()
        return jsonify({"message": "Horario actualizado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.delete('/api/horario/<string:id_horario>')
def delete_horario(id_horario):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM horario WHERE id_horario = %s", (id_horario,))
        conn.commit()
        return jsonify({"message": "Horario eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
###########################################################
@app.get('/api/bitacora_personal')
def get_bitacora_personal():
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT bitacora_personal.*, empleado.nombre AS empleado_nombre
            FROM bitacora_personal
            LEFT JOIN empleado ON bitacora_personal.id_empleado = empleado.id_empleado
        """)
        bitacora = cursor.fetchall()
        return jsonify(bitacora)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/bitacora_personal')
def create_bitacora_personal():
    try:
        id_empleado = request.json.get('id_empleado')
        accion = request.json.get('accion')
        if not id_empleado or not accion:
            return jsonify({"error": "Los campos 'id_empleado' y 'accion' son requeridos"}), 400
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_bitacora FROM bitacora_personal ORDER BY id_bitacora DESC LIMIT 1")
        last_id = cursor.fetchone()
        if last_id:
            last_num = int(last_id[0][1:])
            nuevo_id = f"B{last_num + 1:03d}"
        else:
            nuevo_id = "B001"
        cursor.execute("""
            INSERT INTO bitacora_personal (id_bitacora, id_empleado, accion)
            VALUES (%s, %s, %s)
        """, (nuevo_id, id_empleado, accion))
        conn.commit()
        return jsonify({"message": "Bitácora personal creada exitosamente", "id_bitacora": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/bitacora_personal/<string:id_bitacora>')
def update_bitacora_personal(id_bitacora):
    try:
        id_empleado = request.json.get('id_empleado')
        accion = request.json.get('accion')
        if not id_empleado and not accion:
            return jsonify({"error": "Se requiere al menos uno de los campos 'id_empleado' o 'accion'}"}), 400
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("SELECT id_bitacora FROM bitacora_personal WHERE id_bitacora = %s", (id_bitacora,))
        if cursor.fetchone() is None:
            return jsonify({"error": f"No se encontró la bitácora con el id {id_bitacora}"}), 404
        update_values = []
        query = "UPDATE bitacora_personal SET"
        if id_empleado:
            query += " id_empleado = %s,"
            update_values.append(id_empleado)
        if accion:
            query += " accion = %s,"
            update_values.append(accion)
        query = query.rstrip(',')
        query += " WHERE id_bitacora = %s"
        update_values.append(id_bitacora)
        cursor.execute(query, tuple(update_values))
        conn.commit()
        return jsonify({"message": "Bitácora personal actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.delete('/api/bitacora_personal/<string:id_bitacora_personal>')
def delete_bitacora_personal(id_bitacora_personal):
    try:
        conn = get_connection(base_datos_personal)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bitacora_personal WHERE id_bitacora_personal = %s", (id_bitacora_personal,))
        conn.commit()
        return jsonify({"message": "Rol eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

################################################
"""
@app.get('/api/rol')
def get_roles():
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rol")
        roles = cursor.fetchall()
        return jsonify(roles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/rol')
def create_rol():
    descripcion = request.json.get('descripcion')
    estatus = request.json.get('estatus')
    if not descripcion or not estatus:
        return jsonify({"error": "Los campos 'descripcion' y 'estatus' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rol (id_rol, descripcion, estatus) VALUES (UUID(), %s, %s)",
            (descripcion, estatus)
        )
        conn.commit()
        return jsonify({"message": "Rol creado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.delete('/api/rol/<string:id_rol>')
def delete_rol(id_rol):
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rol WHERE id_rol = %s", (id_rol,))
        conn.commit()
        return jsonify({"message": "Rol eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/rol/<string:id_rol>')
def update_rol(id_rol):
    descripcion = request.json.get('descripcion')
    estatus = request.json.get('estatus')
    if not descripcion or not estatus:
        return jsonify({"error": "Los campos 'descripcion' y 'estatus' son requeridos"}), 400
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE rol SET descripcion = %s, estatus = %s WHERE id_rol = %s",
            (descripcion, estatus, id_rol)
        )
        conn.commit()
        return jsonify({"message": "Rol actualizado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.get('/api/rol/<string:id_rol>')
def get_rol(id_rol):
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rol WHERE id_rol = %s", (id_rol,))
        rol = cursor.fetchone()
        if rol:
            return jsonify(rol)
        return jsonify({"error": "Rol no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
"""
        
############################################################
@app.get('/api/usuario')
def get_usuarios():
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT usuario.*, rol.descripcion AS rol_descripcion
            FROM usuario
            LEFT JOIN rol ON usuario.id_rol = rol.id_rol
        """)
        usuarios = cursor.fetchall()
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/usuario')
def create_usuario():
    try:
        nombre_usuario = request.json.get('nombre_usuario')
        contrasena = request.json.get('contrasena')
        id_rol = request.json.get('id_rol', None)
        estatus = request.json.get('estatus', 'activo')
        if not nombre_usuario or not contrasena or not estatus:
            return jsonify({"error": "Los campos 'nombre_usuario', 'contrasena' y 'estatus' son requeridos"}), 400
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario FROM usuario ORDER BY id_usuario DESC LIMIT 1")
        last_id = cursor.fetchone()
        if last_id:
            last_id_num = int(last_id['id_usuario'][1:])
            new_id_num = last_id_num + 1
            new_id_usuario = f'U{new_id_num:03}'
        else:
            new_id_usuario = 'U001'
        cursor.execute("""
            INSERT INTO usuario (id_usuario, nombre_usuario, contrasena, id_rol, estatus)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_id_usuario, nombre_usuario, contrasena, id_rol, estatus))
        conn.commit()
        return jsonify({"message": f"Usuario {new_id_usuario} creado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.delete('/api/usuario/<string:id_usuario>')
def delete_usuario(id_usuario):
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        return jsonify({"message": "Usuario eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/usuario/<string:id_usuario>')
def update_usuario(id_usuario):
    try:
        nombre_usuario = request.json.get('nombre_usuario')
        contrasena = request.json.get('contrasena')
        id_rol = request.json.get('id_rol', None)
        estatus = request.json.get('estatus', 'activo')
        if not nombre_usuario or not contrasena or not estatus:
            return jsonify({"error": "Los campos 'nombre_usuario', 'contrasena' y 'estatus' son requeridos"}), 400
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,))
        usuario_existente = cursor.fetchone()
        if not usuario_existente:
            return jsonify({"error": "Usuario no encontrado"}), 404
        cursor.execute("""
            UPDATE usuario 
            SET nombre_usuario = %s, contrasena = %s, id_rol = %s, estatus = %s 
            WHERE id_usuario = %s
        """, (nombre_usuario, contrasena, id_rol, estatus, id_usuario))
        conn.commit()
        return jsonify({"message": f"Usuario {id_usuario} actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

############################################################
@app.get('/api/bitacora_seguridad')
def get_bitacora_seguridad():
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT bitacora_seguridad.*, usuario.nombre_usuario AS usuario_nombre
            FROM bitacora_seguridad 
            LEFT JOIN usuario ON bitacora_seguridad.id_usuario = usuario.id_usuario
        """)
        bitacora = cursor.fetchall()
        return jsonify(bitacora)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.post('/api/bitacora_seguridad')
def create_bitacora_seguridad():
    try:
        accion = request.json.get('accion')
        id_usuario = request.json.get('id_usuario')
        if not accion or not id_usuario:
            return jsonify({"error": "Los campos 'accion' y 'id_usuario' son requeridos"}), 400
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_bitacora FROM bitacora_seguridad ORDER BY id_bitacora DESC LIMIT 1")
        last_id_result = cursor.fetchone()
        if last_id_result:
            last_id = last_id_result['id_bitacora']
            next_id_int = int(last_id[1:]) + 1
            next_id = f"B{next_id_int:03d}"
        else:
            next_id = "B001"
        cursor.execute("""
            INSERT INTO bitacora_seguridad (id_bitacora, id_usuario, accion)
            VALUES (%s, %s, %s)
        """, (next_id, id_usuario, accion))
        conn.commit()
        return jsonify({"message": "Bitácora de seguridad creada exitosamente", "id_bitacora": next_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.put('/api/bitacora_seguridad/<string:id_bitacora>')
def update_bitacora_seguridad(id_bitacora):
    try:
        accion = request.json.get('accion')
        id_usuario = request.json.get('id_usuario')
        if not accion or not id_usuario:
            return jsonify({"error": "Los campos 'accion' y 'id_usuario' son requeridos"}), 400
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_bitacora FROM bitacora_seguridad WHERE id_bitacora = %s", (id_bitacora,))
        existing_bitacora = cursor.fetchone()
        if not existing_bitacora:
            return jsonify({"error": "No se encontró la bitácora con el id proporcionado"}), 404
        cursor.execute("""
            UPDATE bitacora_seguridad
            SET id_usuario = %s, accion = %s
            WHERE id_bitacora = %s
        """, (id_usuario, accion, id_bitacora))
        conn.commit()
        return jsonify({"message": "Bitácora de seguridad actualizada exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.delete('/api/bitacora_seguridad/<string:id_bitacora>')
def delete_bitacora_seguridad(id_bitacora):
    try:
        conn = get_connection(base_datos_seguridad)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bitacora_seguridad WHERE id_bitacora = %s", (id_bitacora,))
        conn.commit()
        return jsonify({"message": "Bitácora de seguridad eliminada exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.get('/')
def home():
    return send_file('static/index.html')

@app.route('/create-role')
def create_role():
    return send_file('create-role.html')

@app.route('/edit-role')
def edit_role():
    return render_template('edit-role.html')

if __name__ == '__main__':
    app.run(debug=True)
