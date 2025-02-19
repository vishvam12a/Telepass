import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import rsa
import base64
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Set the authorized user ID (Replace with your Telegram user ID)
AUTHORIZED_USER_ID = 1642918544  # Replace with your actual Telegram user ID

# Decorator to check user authorization
def authorized_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != AUTHORIZED_USER_ID:
            await update.message.reply_text("Unauthorized access. This bot is private.")
            return
        return await func(update, context)
    return wrapper

# Initialize RSA keys
def generate_keys():
    if not os.path.exists('private.pem') or not os.path.exists('public.pem'):
        (pubkey, privkey) = rsa.newkeys(2048)
        with open('private.pem', 'wb') as f:
            f.write(privkey.save_pkcs1('PEM'))
        with open('public.pem', 'wb') as f:
            f.write(pubkey.save_pkcs1('PEM'))
    
    with open('public.pem', 'rb') as f:
        pubkey = rsa.PublicKey.load_pkcs1(f.read())
    with open('private.pem', 'rb') as f:
        privkey = rsa.PrivateKey.load_pkcs1(f.read())
    
    return pubkey, privkey

# Password manager class
class PasswordManager:
    def __init__(self):
        self.passwords: Dict[str, Dict[str, str]] = {}
        self.pubkey, self.privkey = generate_keys()
        self.load_passwords()

    def encrypt(self, text: str) -> str:
        encrypted = rsa.encrypt(text.encode(), self.pubkey)
        return base64.b64encode(encrypted).decode()

    def decrypt(self, encrypted_text: str) -> str:
        try:
            encrypted = base64.b64decode(encrypted_text)
            decrypted = rsa.decrypt(encrypted, self.privkey)
            return decrypted.decode()
        except:
            return ""

    def add_password(self, user_id: str, service: str, password: str) -> bool:
        if user_id not in self.passwords:
            self.passwords[user_id] = {}
        
        self.passwords[user_id][service] = self.encrypt(password)
        self.save_passwords()
        return True

    def get_password(self, user_id: str, service: str) -> Optional[str]:
        if user_id in self.passwords and service in self.passwords[user_id]:
            return self.decrypt(self.passwords[user_id][service])
        return None

    def delete_password(self, user_id: str, service: str) -> bool:
        if user_id in self.passwords and service in self.passwords[user_id]:
            del self.passwords[user_id][service]
            self.save_passwords()
            return True
        return False

    def list_services(self, user_id: str) -> list:
        if user_id in self.passwords:
            return list(self.passwords[user_id].keys())
        return []

    def save_passwords(self):
        with open('passwords.json', 'w') as f:
            json.dump(self.passwords, f)

    def load_passwords(self):
        try:
            with open('passwords.json', 'r') as f:
                self.passwords = json.load(f)
        except FileNotFoundError:
            self.passwords = {}

# Initialize password manager
password_manager = PasswordManager()

# Bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Secure Password Manager Bot!\n\n"
        "Commands:\n"
        "/add <service> <password> - Add a new password\n"
        "/get <service> - Get a password\n"
        "/delete <service> - Delete a password\n"
        "/list - List all services"
    )

async def add_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add <service> <password>")
        return

    service = context.args[0]
    password = ' '.join(context.args[1:])
    user_id = str(update.effective_user.id)

    if password_manager.add_password(user_id, service, password):
        await update.message.reply_text(f"Password for {service} has been securely stored.")
    else:
        await update.message.reply_text("Failed to store password.")

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /get <service>")
        return

    service = context.args[0]
    user_id = str(update.effective_user.id)
    password = password_manager.get_password(user_id, service)

    if password:
        await update.message.reply_text(f"Password for {service}: {password}")
    else:
        await update.message.reply_text(f"No password found for {service}")

async def delete_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /delete <service>")
        return

    service = context.args[0]
    user_id = str(update.effective_user.id)

    if password_manager.delete_password(user_id, service):
        await update.message.reply_text(f"Password for {service} has been deleted.")
    else:
        await update.message.reply_text(f"No password found for {service}")

async def list_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    services = password_manager.list_services(user_id)

    if services:
        await update.message.reply_text("Your stored services:\n" + "\n".join(services))
    else:
        await update.message.reply_text("You have no stored passwords.")

def main():
    # Replace with your bot token
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_password))
    application.add_handler(CommandHandler("get", get_password))
    application.add_handler(CommandHandler("delete", delete_password))
    application.add_handler(CommandHandler("list", list_services))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
