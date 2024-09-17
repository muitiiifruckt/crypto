import sqlite3
db = sqlite3.connect("bitcoin.db")

cursor = db.cursor()

cursor.execute(""" 

    CREATE TABLE IF NOT EXISTS price_monitoring (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,                       -- Название валютной пары (например, BTC/USDT)
    price           DECIMAL(18, 8) NOT NULL,             -- Текущая цена
    max_price       DECIMAL(18, 8),                      -- Максимальная цена за период мониторинга
    min_price       DECIMAL(18, 8),                      -- Минимальная цена за период мониторинга
    date            TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Дата и время записи в формате ISO
    difference      DECIMAL(18, 8),                      -- Разница цены в процентах с момента последней записи
    total_amount    DECIMAL(18, 8)                       -- Общая сумма накоплений в валюте
                );
                        """)

db.commit()

db.close()