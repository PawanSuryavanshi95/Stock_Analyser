import csv

def read_db():
    with open('db.csv', 'r') as f:
        rows = f.readlines()
    
    rows = [x.split('\n')[0] for x in rows]

    return rows

def add_db(stock_name):

    rows = read_db()

    if not stock_name in rows:

        with open('db.csv', 'a') as f:

            write = csv.writer(f)
            write.writerows([[stock_name]])
        
        return True
    
    return False

def remove_db(stock_name):

    rows = read_db()

    if stock_name in rows:

        rows.remove(stock_name)

        rows = [[x] for x in rows]

        with open('db.csv', 'w') as f:

            write = csv.writer(f)
            write.writerows(rows)
        
        return True
    
    return False
