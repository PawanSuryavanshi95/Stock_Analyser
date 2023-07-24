import csv

from common import STOCK_FILE_PATH, PREFERENCES_FILE_PATH

async def read_db():
    with open(STOCK_FILE_PATH, 'r') as f:
        rows = f.readlines()
    
    rows = [x.split('\n')[0] for x in rows]

    return rows

async def add_db(stock_name):

    rows = await read_db()

    if not stock_name in rows:

        with open(STOCK_FILE_PATH, 'a') as f:

            write = csv.writer(f)
            write.writerows([[stock_name]])
        
        return True
    
    return False

async def remove_db(stock_name):

    rows = await read_db()

    if stock_name in rows:

        rows.remove(stock_name)

        rows = [[x] for x in rows]

        with open(STOCK_FILE_PATH, 'w') as f:

            write = csv.writer(f)
            write.writerows(rows)
        
        return True
    
    return False

async def get_preferences():
    with open(PREFERENCES_FILE_PATH, 'r') as f:
        rows = f.readlines()
    
    rows = [x.split('\n')[0] for x in rows]

    return rows

async def update_preferences(candle_size, duration):

    with open(PREFERENCES_FILE_PATH, 'w') as f:

            write = csv.writer(f)
            write.writerows([[candle_size], [duration]])