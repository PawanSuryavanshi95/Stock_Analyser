Setup :

Go to project directory and run these commands

```
pipenv install
pipenv shell
```

To run in dev mode :

```
sanic app --host=127.0.0.1 --port=8000 --debug --reload
```

Available Routes :

```
v1/analyse/historical-data/<stock_symbol>
v1/analyse/compare/<stock_symbol_1>&<stock_symbol_2>
v1/analyse/real-time/<stock_symbol>
```
