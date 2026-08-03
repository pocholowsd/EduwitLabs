from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import mysql.connector
import json

app = Flask(__name__)
CORS(app) 

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'eduwit_go'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/api/categorias', methods=['GET'])
def get_categorias():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    conn.close()
    return jsonify(categorias)

@app.route('/api/categorias', methods=['POST'])
def add_categoria():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categorias (nombre, color) VALUES (%s, %s)", (data['name'], data['color']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'name': data['name'], 'color': data['color']})

@app.route('/api/programas', methods=['GET'])
def get_programas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM programas")
    programas = cursor.fetchall()
    conn.close()
    
    for p in programas:
        if isinstance(p['json_data'], str):
            p['json_data'] = json.loads(p['json_data'])
        p['disabled'] = not bool(p['estado']) 
        p['categoryId'] = p['categoria_id']
        p['name'] = p['nombre']
    return jsonify(programas)

@app.route('/api/programas', methods=['POST'])
def add_programa():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    json_str = json.dumps(data['jsonData'])
    version_actual = datetime.now().strftime('%d%m%y.%H%M')

    cursor.execute("INSERT INTO programas (categoria_id, nombre, json_data, version) VALUES (%s, %s, %s, %s)",
                   (data['categoryId'], data['name'], json_str, version_actual))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'version': version_actual})

@app.route('/api/programas/<int:id>', methods=['PUT'])
def update_programa(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    version_actual = datetime.now().strftime('%d%m%y.%H%M')
    
    if 'disabled' in data:
        estado = 0 if data['disabled'] else 1
        cursor.execute("UPDATE programas SET estado = %s, version = %s WHERE id = %s", (estado, version_actual, id))
    else: 
        json_str = json.dumps(data['jsonData'])
        cursor.execute("UPDATE programas SET categoria_id = %s, nombre = %s, json_data = %s, version = %s WHERE id = %s",
                       (data['categoryId'], data['name'], json_str, version_actual, id))
    
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'version': version_actual})

@app.route('/api/exportar-arduino', methods=['GET'])
def exportar_arduino():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.id, p.nombre as name, p.version, p.json_data, c.nombre as cat_name 
        FROM programas p 
        JOIN categorias c ON p.categoria_id = c.id 
        WHERE p.estado = 1
        ORDER BY c.id ASC, p.id ASC
    """)
    resultados = cursor.fetchall()
    conn.close()
    
    agrupados = {}
    for row in resultados:
        categoria = row['cat_name']
        if categoria not in agrupados:
            agrupados[categoria] = []
            
        agrupados[categoria].append({
            "id": row['id'],
            "name": row['name'],
            "version": row['version'],
            "data": json.loads(row['json_data']) if isinstance(row['json_data'], str) else row['json_data']
        })

    return Response(json.dumps(agrupados, separators=(',', ':')), mimetype='application/json')

@app.route('/api/check-updates', methods=['POST'])
def check_updates():
    versiones_locales = request.json or {}
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, version FROM programas WHERE estado = 1")
    db_programas = cursor.fetchall()
    conn.close()
    
    actualizaciones = []
    for row in db_programas:
        id_str = str(row['id'])
        version_bd = row['version']

        if id_str not in versiones_locales or versiones_locales[id_str] < version_bd:
            actualizaciones.append(row['id'])
            
    return jsonify({
        "update_available": len(actualizaciones) > 0,
        "pending_ids": actualizaciones
    })

@app.route('/api/programas/<int:id>', methods=['GET'])
def get_programa_especifico(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.id, p.nombre as name, p.version, p.json_data, c.nombre as cat_name 
        FROM programas p 
        JOIN categorias c ON p.categoria_id = c.id 
        WHERE p.id = %s AND p.estado = 1
    """, (id,))
    
    programa = cursor.fetchone()
    conn.close()
    
    if programa:
        respuesta = {
            "id": programa['id'],
            "name": programa['name'],
            "version": programa['version'],
            "categoria": programa['cat_name'],
            "data": json.loads(programa['json_data']) if isinstance(programa['json_data'], str) else programa['json_data']
        }
        return Response(json.dumps(respuesta, separators=(',', ':')), mimetype='application/json')
    else:
        return jsonify({"error": "Programa no encontrado o está deshabilitado"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)