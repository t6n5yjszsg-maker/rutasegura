import os
import threading
from flask import Flask, render_template
import bot_pruebas

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")

if __name__ == "__main__":
    hilo_bot = threading.Thread(target=lambda: bot_pruebas.bot.polling(none_stop=True), daemon=True)
    hilo_bot.start()
    print("TODO PRENDIDO: Web + Bot")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)