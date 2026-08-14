import os
import requests
import fal_client
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FAL_KEY = os.getenv("FAL_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Envíame una imagen junto con las instrucciones de cómo quieres animarla en la descripción.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
