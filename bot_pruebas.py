import os
import requests
import telebot

TOKEN = '8894198822:AAE_gfFxVbdP4OOQVPMFPJScbgMSJnIGo6s'
bot = telebot.TeleBot(TOKEN)

ZONAS = {
    "cutervo": {"nombre": "Cutervo", "lat": -6.3814, "lon": -78.8189, "alerta": "Crecida del río Callayuc colapsó la plataforma. Ruta alterna: Cutervo - Socota - San Andrés"},
    "chiple": {"nombre": "Cutervo - Chiple", "lat": -6.3814, "lon": -78.8189, "alerta": "Crecida del río Callayuc colapsó la plataforma. Ruta alterna: Cutervo - Socota - San Andrés"},
    "san miguel": {"nombre": "San Miguel", "lat": -6.9972, "lon": -78.8658, "alerta": "Deslizamiento de más de 100m en Los Ajos. Ruta alterna: San Miguel - Kuntur Wasi"},
    "los ajos": {"nombre": "San Miguel - Los Ajos", "lat": -6.9972, "lon": -78.8658, "alerta": "Deslizamiento de más de 100m. Ruta alterna: San Miguel - Kuntur Wasi"},
    "chota": {"nombre": "Chota", "lat": -6.5574, "lon": -78.6536, "alerta": "Lluvias intensas y deslizamientos leves. Ruta alterna: Chota - Bambamarca"},
    "jaen": {"nombre": "Jaén", "lat": -5.7089, "lon": -78.8075, "alerta": "Vía transitable con precaución por lluvias leves."},
    "jaén": {"nombre": "Jaén", "lat": -5.7089, "lon": -78.8075, "alerta": "Vía transitable con precaución por lluvias leves."},
    "cajamarca": {"nombre": "Cajamarca", "lat": -7.16378, "lon": -78.50027, "alerta": "Lluvias persistentes. Transitable con precaución."},
    "piura": {"nombre": "Piura", "lat": -5.19449, "lon": -80.63282, "alerta": "Crecida del río Piura y aniegos urbanos. Aléjate de riberas y zonas bajas. Usa pasos elevados autorizados."},
    "castilla": {"nombre": "Castilla - Piura", "lat": -5.1985, "lon": -80.6150, "alerta": "Anegamiento por desborde del río Piura. Calles inundadas, evacuar a zonas altas."},
    "catacaos": {"nombre": "Catacaos - Piura", "lat": -5.2668, "lon": -80.6718, "alerta": "Inundación por crecida del río Piura. Vías de acceso bloqueadas. Ruta alterna: Vía de evacuación a Piura centro."},
    "huancabamba": {"nombre": "Huancabamba", "lat": -5.2427, "lon": -79.4475, "alerta": "Deslizamientos y vías bloqueadas por lluvias. No viajar de noche."},
    "ayabaca": {"nombre": "Ayabaca", "lat": -4.6386, "lon": -79.7123, "alerta": "Lluvias y neblina intensa. Transitable solo de día."},
}

def clima_tiempo_real(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&timezone=auto"
        r = requests.get(url, timeout=10).json()
        c = r["current"]
        codigo = c["weather_code"]
        if codigo in [0,1]: desc = "despejado"
        elif codigo in [2,3]: desc = "nublado"
        elif codigo in [45,48]: desc = "neblina"
        elif codigo in [51,53,55,61,63,65,80,81,82]: desc = "lluvia"
        elif codigo in [95,96,99]: desc = "tormenta"
        else: desc = "nublado"
        return desc, c["temperature_2m"], c["relative_humidity_2m"], c["precipitation"], c["wind_speed_10m"]
    except:
        return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "¡Hola! 👋 Soy **RutaSegura Niño** 🚨\n\n"
        "Escribe tu zona (*Cutervo, Chota, Jaén, San Miguel, Cajamarca, Piura, Castilla, Catacaos, Huancabamba, Ayabaca*) y te digo el clima EN TIEMPO REAL, si la ruta está TRANSITABLE, en PRECAUCIÓN o BLOQUEADO, y te mando tu mapa de refugio.",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: True)
def responder_usuario(message):
    texto = message.text.lower()
    if any(p in texto for p in ["hola", "buenas"]):
        bot.reply_to(message, "¡Hola! 😊 Escribe tu provincia y te doy su alerta en tiempo real.")
        return
    if any(p in texto for p in ["gracias", "ok", "listo"]):
        bot.reply_to(message, "¡De nada! 👍 Mantén la calma y prioriza tu seguridad.")
        return

    zona_key = None
    for k in ZONAS:
        if k in texto:
            zona_key = k
            break
    if not zona_key:
        bot.reply_to(message, "💡 Escribe: **Cutervo, Chota, Jaén, San Miguel, Cajamarca, Piura, Castilla, Catacaos, Huancabamba, Ayabaca**", parse_mode='Markdown')
        return

    info = ZONAS[zona_key]
    clima = clima_tiempo_real(info["lat"], info["lon"])
    if clima is None:
        bot.reply_to(message, "⚠️ No pude consultar el clima ahora, intenta en 1 min.")
        return

    desc, temp, humedad, lluvia, viento = clima

    if desc in ["lluvia", "tormenta"] or lluvia > 2:
        estado = "🔴 BLOQUEADO - ALERTA ROJA"
        consejo = "No pases por la ruta, riesgo de deslizamiento. Ve a zona alta y espera."
    elif desc in ["nublado", "neblina"] or lluvia > 0:
        estado = "⚠️ PRECAUCIÓN - ALERTA AMARILLA"
        consejo = "Maneja con cuidado, posible lluvia y piedras en la vía."
    else:
        estado = "🟢 TRANSITABLE"
        consejo = "Ruta libre por ahora, pero igual mantente atento."

    mensaje = (
        f"{estado}\n\n"
        f"📍 Zona: **{info['nombre']}**\n"
        f"🌦️ Clima ahora mismo: **{desc}**\n"
        f"🌡️ Temperatura: **{temp}°C**\n"
        f"💧 Humedad: **{humedad}%**\n"
        f"🌧️ Lluvia: **{lluvia} mm**\n"
        f"💨 Viento: **{viento} km/h**\n\n"
        f"🚨 Alerta de tu zona: **{info['alerta']}**\n\n"
        f"👉 {consejo}\n\n"
        f"📍 *Aquí tienes tu mapa de refugio:*"
    )
    bot.reply_to(message, mensaje, parse_mode='Markdown')
    bot.send_location(message.chat.id, latitude=info["lat"], longitude=info["lon"])

print("Bot en tiempo real prendido...")
if __name__ == "__main__":
    bot.polling(none_stop=True)