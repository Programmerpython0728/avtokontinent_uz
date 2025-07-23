from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST, require_GET
from .models import Cart, CartItem, Order, OrderItem, PaymentCard
from shop.models import Product
from telegram_bot.utils import send_order_status_update


def get_or_create_cart(request):
    try:
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_key=request.session.session_key,
                user=None
            )
        return cart
    except Exception as e:
        messages.error(request, _("Savatni yuklashda xatolik yuz berdi: ") + str(e)) # Xato xabari o'zgartirildi
        raise


@require_POST
def add_to_cart(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'message': _('Mahsulot savatga qo\'shildi!')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': _('Xatolik yuz berdi: ') + str(e)
        }, status=500)

@require_GET
def cart_count(request):
    try:
        cart = get_or_create_cart(request)
        return JsonResponse({
            'success': True,
            'count': cart.get_total_items()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'count': 0
        }, status=400)

def cart_view(request):
    try:
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')

        context = {
            'cart': cart,
            'cart_items': cart_items,
        }
        return render(request, 'orders/cart.html', context)

    except Exception as e:
        messages.error(request, _("Savatingizni yuklashda xatolik yuz berdi: ") + str(e)) # Xato xabari o'zgartirildi
        return render(request, 'orders/cart.html', {'cart_items': []})


@require_POST
def update_cart_item(request, item_id):
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        action = request.POST.get('action')

        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            cart_item.quantity -= 1
        elif action == 'remove':
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Mahsulot savatdan olib tashlandi'
            })

        cart_item.save()

        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'total_price': cart_item.get_total_price()
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def checkout(request):
    try:
        request.session['next_url'] = 'orders:checkout'
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')

        if not cart_items.exists():
            messages.warning(request, _('Savatingiz bo\'sh!'))
            return redirect('orders:cart')

        payment_card = PaymentCard.objects.filter(is_active=True).first()

        if request.method == 'POST':
            if not request.POST.get('oferta_accepted'):
                messages.error(request, _('Oferta shartlarini qabul qilishingiz kerak!'))
                return render(request, 'orders/checkout.html', {
                    'cart': cart,
                    'cart_items': cart_items,
                    'payment_card': payment_card,
                })

            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.get_total_price(),
                payment_card=payment_card,
                delivery_address=request.POST.get('delivery_address', ''),
                notes=request.POST.get('notes', ''),
                oferta_accepted=True
            )

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.get_price_uzs()
                )

            cart_items.delete()

            messages.success(request, _('Buyurtma muvaffaqiyatli yaratildi!'))
            send_order_status_update(order, 'order_created')
            return redirect('orders:order_detail', order_id=order.id)

        context = {
            'cart': cart,
            'cart_items': cart_items,
            'payment_card': payment_card,
        }
        return render(request, 'orders/checkout.html', context)

    except Exception as e:
        messages.error(request, _('Checkout jarayonida xatolik yuz berdi: ') + str(e)) # Xato xabari o'zgartirildi
        return redirect('orders:cart')


@login_required
def order_detail(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if request.method == 'POST' and 'payment_receipt' in request.FILES:
            order.payment_receipt = request.FILES['payment_receipt']
            order.status = 'payment_uploaded'
            order.save()

            send_order_status_update(order, 'payment_uploaded')
            messages.success(request, _('To\'lov cheki yuklandi! Tez orada tekshirib ko\'ramiz.'))

        return render(request, 'orders/order_detail.html', {'order': order})

    except Exception as e:
        messages.error(request, _('Buyurtma ma\'lumotlarini ko\'rsatishda xatolik: ') + str(e)) # Xato xabari o'zgartirildi
        return redirect('orders:order_list')


@login_required
def order_list(request):
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'orders/order_list.html', {'orders': orders})
    except Exception as e:
        messages.error(request, _('Buyurtmalar ro\'yxatini ko\'rsatishda xatolik: ') + str(e)) # Xato xabari o'zgartirildi
        return render(request, 'orders/order_list.html', {'orders': []})