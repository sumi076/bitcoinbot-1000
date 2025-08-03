import logging
import time
import requests
from telegram import Bot
from telegram.error import TelegramError

# CONFIGURATION
BOT_TOKEN = "8127163050:AAHbKsUB6Ou2vHw-QvghsKZdr0FXmkfQSMY"
CHAT_ID = "-1002735848978"  # e.g., "-1001234567890" or "@mygroup"
CHECK_INTERVAL = 60  # seconds between price checks
THRESHOLD = 1000.0  # USD variation threshold
API_URL = "https://api.coingecko.com/api/v3/simple/price"

# Initialize bot and logging
bot = Bot(token=BOT_TOKEN)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_btc_price():
    """
    Fetch current Bitcoin price in USD from CoinGecko.
    """
    try:
        resp = requests.get(API_URL, params={
            'ids': 'bitcoin',
            'vs_currencies': 'usd'
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return float(data['bitcoin']['usd'])
    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error(f"Error fetching BTC price: {e}")
        return None


def main():
    last_price = get_btc_price()
    if last_price is None:
        logger.error("Could not get initial BTC price. Exiting.")
        return

    logger.info(f"Starting price monitor. Initial price: ${last_price:.2f}")
    
    while True:
        time.sleep(CHECK_INTERVAL)
        current_price = get_btc_price()
        if current_price is None:
            continue

        variation = abs(current_price - last_price)
        if variation >= THRESHOLD:
            message = (
                f"Bitcoin price alert!\n"
                f"Previous: ${last_price:,.2f}\n"
                f"Current: ${current_price:,.2f}\n"
                f"Change: ${current_price - last_price:,.2f}"
            )
            try:
                bot.send_message(chat_id=CHAT_ID, text=message)
                logger.info(f"Sent alert: {message}")
            except TelegramError as e:
                logger.error(f"Failed to send message: {e}")
            # Reset last_price to current after alert
            last_price = current_price
        else:
            logger.debug(f"Variation ${variation:.2f} below threshold.")


if __name__ == '__main__':
    main()
