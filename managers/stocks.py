import csv

async def read_db():
    with open('db/stocks.csv', 'r') as f:
        rows = f.readlines()
    
    rows = [x.split('\n')[0] for x in rows]

    return rows

async def add_db(stock_name):

    rows = await read_db()

    if not stock_name in rows:

        with open('db/stocks.csv', 'a') as f:

            write = csv.writer(f)
            write.writerows([[stock_name]])
        
        return True
    
    return False

async def remove_db(stock_name):

    rows = await read_db()

    if stock_name in rows:

        rows.remove(stock_name)

        rows = [[x] for x in rows]

        with open('db/stocks.csv', 'w') as f:

            write = csv.writer(f)
            write.writerows(rows)
        
        return True
    
    return False

async def get_preferences():
    with open('db/preferences.csv', 'r') as f:
        rows = f.readlines()
    
    rows = [x.split('\n')[0] for x in rows]

    return rows

async def update_preferences(candle_size, duration):

    with open('db/preferences.csv', 'w') as f:

            write = csv.writer(f)
            write.writerows([[candle_size], [duration]])