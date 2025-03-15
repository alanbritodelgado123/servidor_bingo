from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import random
import string

app = Flask(__name__)
socketio = SocketIO(app)

# Estado del juego
numeros_generados = []
cartones = {}
jugadores = {}  # Almacena la información de los jugadores

# Función para generar un identificador único (letra y número)
def generar_identificador_unico():
    while True:
        numero = random.randint(1, 100)
        letra = random.choice(string.ascii_uppercase)
        identificador = f"{letra}-{numero}"
        if identificador not in jugadores.values():
            return identificador

# Ruta para registrar un jugador
@app.route('/registrar_jugador', methods=['POST'])
def registrar_jugador():
    data = request.json
    nombre = data["nombre"]
    identificador = generar_identificador_unico()
    jugadores[nombre] = identificador
    return jsonify({"nombre": nombre, "identificador": identificador})

# Ruta para generar un cartón
@app.route('/generar_carton', methods=['POST'])
def generar_carton():
    data = request.json
    nombre = data["nombre"]
    carton = random.sample(range(1, 100), 15)  # Genera 15 números únicos
    carton_id = len(cartones) + 1
    cartones[carton_id] = {"nombre": nombre, "numeros": carton, "marcados": []}
    return jsonify({"carton_id": carton_id, "carton": carton})

# Ruta para generar un número aleatorio
@app.route('/generar_numero', methods=['GET'])
def generar_numero():
    numero = random.randint(1, 100)
    numeros_generados.append(numero)
    socketio.emit('nuevo_numero', {'numero': numero}, broadcast=True)
    return jsonify({"numero": numero})

# Ruta para marcar un número en un cartón
@app.route('/marcar_numero', methods=['POST'])
def marcar_numero():
    data = request.json
    carton_id = data["carton_id"]
    numero = data["numero"]

    if numero not in numeros_generados:
        return jsonify({"status": "error", "mensaje": "Este número no ha salido todavía."})

    if numero in cartones[carton_id]["numeros"]:
        cartones[carton_id]["marcados"].append(numero)
        socketio.emit('numero_marcado', {'carton_id': carton_id, 'numero': numero}, broadcast=True)
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "mensaje": "Número no válido para este cartón."})

# Ruta para verificar si hay un ganador
@app.route('/verificar_ganador', methods=['GET'])
def verificar_ganador():
    for carton_id, carton in cartones.items():
        if set(carton["marcados"]) == set(carton["numeros"]):
            socketio.emit('partida_terminada', {'ganador': carton["nombre"]}, broadcast=True)
            return jsonify({"ganador": carton["nombre"]})
    return jsonify({"status": "no_ganador"})

# Manejar la conexión de un cliente
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

# Iniciar el servidor
if __name__ == '__main__':
    print("Servidor de Bingo iniciado en http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)