import sqlite3
import aiohttp
import asyncio
from decimal import Decimal
from datetime import datetime
from mailSent import sendEmail

# Пример URL-ов API бирж (в зависимости от биржи могут потребоваться API ключи)
BINANCE_API = 'https://api.binance.com/api/v3/ticker/price?symbol={}'
COINMARKETCAP_API = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={}'
BYBIT_API = 'https://api.bybit.com/v2/public/tickers?symbol={}'
GATEIO_API = 'https://api.gate.io/api2/1/ticker/{}'
KUCOIN_API = 'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={}'

# Функция для подключения к базе данных
def connect_db():
    return sqlite3.connect("bitcoin.db")

# Функция для записи данных в таблицу
def insert_data(pair, price, max_price, min_price, difference, total_amount):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO price_monitoring (title, price, max_price, min_price, date, difference, total_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?) 
    """, (
        pair,
        float(price),         # Преобразование Decimal в float
        float(max_price),     # Преобразование Decimal в float
        float(min_price),     # Преобразование Decimal в float
        datetime.now(),       # текущая дата и время
        float(difference),    # Преобразование Decimal в float
        float(total_amount)   # Преобразование Decimal в float
    ))

    db.commit()
    db.close()

# Асинхронная функция для получения данных с биржи
async def fetch_price(session, url, pair):
    try:
        async with session.get(url) as response:
            data = await response.json()

            # Проверка валидности данных
            if 'price' in data:  # Например, Binance
                return {'symbol': pair, 'price': Decimal(data['price'])}
            elif 'data' in data and data['data'] is not None and 'price' in data['data']:  # Например, KuCoin
                return {'symbol': pair, 'price': Decimal(data['data']['price'])}
            elif 'msg' in data and 'Invalid symbol' in data['msg']:  # Ошибка неверного символа
                print(f"Error: Invalid symbol for pair {pair}")
            elif 'message' in data and 'Error' in data['message']:  # Общая ошибка
                print(f"Error: {data['message']} for pair {pair}")
            else:
                print(f"Unrecognized response for pair {pair}: {data}")
    except Exception as e:
        print(f"Failed to fetch price for {pair}: {e}")
    return None

# Получаем цены для каждой валютной пары
async def get_prices():
    async with aiohttp.ClientSession() as session:
        tasks = []

        # Валютные пары
        pairs = ['BTCUSDT', 'BTCETH', 'BTCXMR', 'BTCSOL', 'BTCRUB', 'BTCDOGE']

        # Список API для разных бирж
        apis = [
            BINANCE_API,
            BYBIT_API,
            GATEIO_API,
            KUCOIN_API
        ]

        # Добавляем запросы для каждой пары на каждой бирже
        for pair in pairs:
            for api in apis:
                tasks.append(fetch_price(session, api.format(pair), pair))

        # Выполняем все запросы одновременно
        responses = await asyncio.gather(*tasks)

        # Фильтруем только корректные данные
        valid_responses = [res for res in responses if res is not None]

        # Записываем данные в базу
        for res in valid_responses:
            pair = res['symbol']
            price = res['price']

            # Получение текущей максимальной и минимальной цены из базы данных
            db = connect_db()
            cursor = db.cursor()

            cursor.execute("SELECT MAX(price), MIN(price) FROM price_monitoring WHERE title=?", (pair,))
            max_min_prices = cursor.fetchone()
            db.close()

            max_price = Decimal(max_min_prices[0]) if max_min_prices[0] else price
            min_price = Decimal(max_min_prices[1]) if max_min_prices[1] else price

            # Рассчитываем разницу (от предыдущей цены)
            difference = (price - max_price) / max_price * 100 if max_price != Decimal(0) else Decimal(0)

            # Общая сумма накоплений (примерный расчет, если у нас 3 BTC)
            total_amount = price * Decimal(3)

            # Записываем данные в базу
            insert_data(pair, price, max_price, min_price, difference, total_amount)
            # Вызов функции sendEmail при выполнении условия
            if difference >= Decimal(0.03):
                subject = "Bitcoin Price Alert"
                body = (
                    f"Pair: {pair}\n"
                    f"Price: {price}\n"
                    f"Max Price: {max_price}\n"
                    f"Min Price: {min_price}\n"
                    f"Difference: {difference}\n"
                    f"Total Amount: {total_amount}"
                )
                sendEmail(
                    subject=subject,
                    body=body,
                    to_email='',  # Замените на реальный email
                    from_email='your-email@example.com'  # Замените на реальный email
                )

        print("Valid responses:", valid_responses)

def start():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_prices())
