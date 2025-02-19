# Secure Telegram Password Manager Bot

A secure password manager bot for Telegram that uses RSA encryption to store passwords safely. The bot provides CRUD (Create, Read, Update, Delete) operations for password management.

## Features

- RSA encryption for password storage
- Secure storage in JSON format
- MITM attack protection through asymmetric encryption
- User-specific password storage
- Basic CRUD operations

## Setup

1. Install required dependencies:
   ```bash
   pip install python-telegram-bot rsa
   ```

2. Replace `YOUR_BOT_TOKEN` in `bot.py` with your Telegram bot token from BotFather.

3. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

- `/start` - Get started with the bot
- `/add <service> <password>` - Add a new password
- `/get <service>` - Retrieve a password
- `/delete <service>` - Delete a password
- `/list` - List all stored services

## Security Features

- RSA 2048-bit encryption
- Separate encryption keys for each bot instance
- User-specific password storage
- No plaintext password storage
- Secure key generation and storage

## Testing

Run the test suite:
```bash
python -m unittest test_password_manager.py
```
## Points to Know

- Create a python venv for running
- You can use any free cloud computing services to host the script 
