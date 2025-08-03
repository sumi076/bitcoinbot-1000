import telebot
import requests
import time
import threading

# 🔐 Reemplaza con tu token real de BotFather
TOKEN = '8127163050:AAHbKsUB6Ou2vHw-QvghsKZdr0FXmkfQSMY'
# 🔐 Reemplaza con tu chat_id (usa @userinfobot para encontrarlo)
CHAT_ID = -1002735848978  # ejemplo: -1001234567890

diferencia_maxima = -100
diferencia_minima = 100  # USD de variación mínima para alerta
intervalo_segundos = 30   # cada cuánto comprobar (segundos)

# Inicializa bot
bot = telebot.TeleBot(TOKEN)

# Estado de las alertas automáticas (True=activadas)
alertas_activas = True
ultimo_precio = None


def obtener_precio_btc():
    """Devuelve precio de BTC en USD usando CoinGecko."""
    resp = requests.get(
        'https://api.coingecko.com/api/v3/simple/price',
        params={'ids': 'bitcoin', 'vs_currencies': 'usd'},
        timeout=10
    )
    resp.raise_for_status()
    return resp.json()['bitcoin']['usd']


@bot.message_handler(commands=['start', 'ayuda'])
def cmd_start(message):
    bot.reply_to(
        message,
        "👋 ¡Bienvenido! Usa /precio para ver el precio de BTC."
        " Usa /activar_alertas y /desactivar_alertas para controlar las alertas automáticas."
    )


@bot.message_handler(commands=['precio'])
def cmd_precio(message):
    precio = obtener_precio_btc()
    bot.reply_to(
        message,
        f"📊 Precio actual de Bitcoin: ${precio:,.2f} USD"
    )


@bot.message_handler(commands=['activar_alertas'])
def cmd_activar(message):
    global alertas_activas
    alertas_activas = True
    bot.reply_to(message, "✅ Alertas automáticas ACTIVADAS. Te avisaré si BTC varía ±$100.")


@bot.message_handler(commands=['desactivar_alertas'])
def cmd_desactivar(message):
    global alertas_activas
    alertas_activas = False
    bot.reply_to(message, "⛔ Alertas automáticas DESACTIVADAS. Ya no recibirás notificaciones.")


def monitorear_cambios():
    global ultimo_precio, alertas_activas
    while True:
        try:
            precio_actual = obtener_precio_btc()
            if ultimo_precio is None:
                ultimo_precio = precio_actual

            # Solo envía alerta si el usuario las ha activado
            elif alertas_activas and abs(precio_actual - ultimo_precio) >= diferencia_minima or (precio_actual - ultimo_precio) <= diferencia_maxima:
                delta = precio_actual - ultimo_precio
                texto = (
                    f"🚨 Bitcoin cambió ${delta:,.2f}!\n"
                    f"Anterior: ${ultimo_precio:,.2f}\n"
                    f"Actual:   ${precio_actual:,.2f}"
                )
                bot.send_message(CHAT_ID, texto)
                ultimo_precio = precio_actual
        except Exception as e:
            print("Error monitoreo:", e)
        time.sleep(intervalo_segundos)


if __name__ == '__main__':
    # Inicia hilo de monitoreo en segundo plano
    hilo = threading.Thread(target=monitorear_cambios, daemon=True)
    hilo.start()
    print("Bot activo. Esperando mensajes y monitoreando precio...")
    # Inicia polling para comandos
    bot.infinity_polling()
