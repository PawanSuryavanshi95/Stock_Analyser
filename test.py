import requests

url = "https://real-time-quotes1.p.rapidapi.com/api/v1/realtime/stock"

querystring = {"symbols":"GAB"}

headers = {
	"X-RapidAPI-Key": "8df590c5ecmsh987bf572c322f98p12fb4bjsn5b4fc10f6825",
	"X-RapidAPI-Host": "real-time-quotes1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())