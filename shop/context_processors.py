from shop.models import Category, CurrencyRate


def categories(request):
    try:
        return {
            'main_categories': Category.objects.filter(is_active=True, parent=None)
        }
    except:
        return {'main_categories': []}

def currency_rate(request):
    try:
        rate = CurrencyRate.objects.first()
        return {
            'currency_rate': rate.usd_to_uzs if rate else 12500
        }
    except:
        return {'currency_rate': 12500}
