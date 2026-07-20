# Telegram Order Detection Bot

Production-ready Telegram bot that monitors all groups where it is added, detects order-related keywords in **message text** and **media captions**, and forwards matching messages to an Orders Group.

## Features

- Built with **python-telegram-bot v22+** (async architecture)
- Monitors every group/supergroup where bot is present
- Detects keywords from:
  - Text messages
  - Photo captions
  - Video captions
  - Document captions
- Case-insensitive keyword detection
- Forwards original message exactly as received
- Prevents duplicate forwarding using `(chat_id, message_id)` cache
- Structured logging to `logs/bot.log`
- Environment-based configuration with `.env`

## Project Structure

- `main.py`
- `config.py`
- `handlers.py`
- `detector.py`
- `keywords.py`
- `utils.py`
- `requirements.txt`
- `.env.example`
- `README.md`
- `logs/` (created automatically at runtime)

## Requirements

- Python 3.12+
- A Telegram bot token from BotFather
- Bot must be added to source groups and have permission to read and forward messages
- Bot must be added to destination orders group

## Installation

```bash
git clone https://github.com/pubgn960/telegram-calculator-bot-orders.git
cd telegram-calculator-bot-orders
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Copy example file and edit values:

```bash
cp .env.example .env
nano .env
```

Set:

- `BOT_TOKEN` = your bot token
- `ORDER_GROUP_ID` = `-1004406625020`
- `IGNORED_USER_IDS` = optional comma-separated Telegram user IDs, for example `123456789,987654321`

## Run Locally

```bash
source .venv/bin/activate
python main.py
```

## Deploy on Ubuntu VPS

### 1) Install system packages

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv git
```

### 2) Clone and setup

```bash
git clone https://github.com/pubgn960/telegram-calculator-bot-orders.git
cd telegram-calculator-bot-orders
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env
```

### 3) Create systemd service

Create `/etc/systemd/system/telegram-order-bot.service`:

```ini
[Unit]
Description=Telegram Order Detection Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram-calculator-bot-orders
Environment="PYTHONUNBUFFERED=1"
ExecStart=/home/ubuntu/telegram-calculator-bot-orders/.venv/bin/python /home/ubuntu/telegram-calculator-bot-orders/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> Replace `User` and paths with your VPS user/path.

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-order-bot
sudo systemctl start telegram-order-bot
sudo systemctl status telegram-order-bot
```

## Logs and Troubleshooting

### View application logs

```bash
tail -f logs/bot.log
```

### View systemd logs

```bash
sudo journalctl -u telegram-order-bot -f
```

### Common issues

1. **Bot not receiving messages**
   - Disable privacy mode via BotFather (`/setprivacy` -> Disable), if group messages are not arriving.
   - Ensure bot is in the group.
2. **Forward fails**
   - Ensure bot is added to Orders Group (`-1004406625020`).
   - Ensure bot has rights to send/forward messages there.
3. **No matches detected**
   - Confirm keywords exist in `keywords.py`.
   - Confirm text/caption contains keyword values.
4. **Environment error**
   - Ensure `.env` exists and includes valid `BOT_TOKEN`.

## Security Notes

- Never commit real `.env` tokens.
- Rotate bot token immediately if leaked.

## License

Private/internal usage.
