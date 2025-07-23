import requests

def get_usd_to_uzs_rate():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = response.json()
        return data['rates'].get('UZS', 12500)
    except Exception as e:
        print(f"Kursni olishda xatolik: {e}")
        return 12500
