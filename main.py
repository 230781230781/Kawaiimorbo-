import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import requests
import fal_client
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Servidor básico para Render
def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FAL_KEY = os.getenv("FAL_KEY")

# 🔒 Candado de seguridad con tu ID de Telegram
ALLOWED_USER_ID = 5757109395

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Acceso denegado. Este bot es de uso privado.")
        return

    await update.message.reply_text("¡Hola! Envíame una imagen junto con las instrucciones de cómo quieres animarla en la descripción.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Acceso denegado. No tienes permiso para usar este bot.")
        return

    prompt = update.message.caption or "Animate this image in high quality"
    await update.message.reply_text("Procesando tu animación, esto puede tomar un momento...")

    photo_file = await update.message.photo[-1].get_file()
    image_url = photo_file.file_path

    try:
        result = fal_client.subscribe(
            "fal-ai/kling-video/v1.5/pro/image-to-video",
            arguments={
                "prompt": prompt,
                "image_url": image_url
            }
        )
        video_url = result.get("video", {}).get("url")
        if video_url:
            await update.message.reply_video(video=video_url)
        else:
            await update.message.reply_text("No se pudo obtener el video.")
    except Exception as e:
        await update.message.reply_text(f"Ocurrió un error: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
