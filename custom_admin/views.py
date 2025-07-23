from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory
from django.contrib.auth import authenticate, login

from shop.models import Category, Product, ProductImage, CarBrand, CarModel, Banner
from orders.models import Order, PaymentCard
from telegram_bot.utils import send_order_status_update
from .forms import CategoryForm, ProductForm, ProductImageForm, OrderStatusForm, CarBrandForm, CarModelForm, \
    CustomAdminLoginForm, BannerForm, PaymentCardForm


def is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('custom_admin:dashboard')

    if request.method == 'POST':
        form = CustomAdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, _('Admin panelga muvaffaqiyatli kirdingiz!'))
                return redirect('custom_admin:dashboard')
            else:
                pass
        else:
            pass
    else:
        form = CustomAdminLoginForm()

    context = {
        'form': form,
        'title': _('Admin Kirish'),
    }
    return render(request, 'custom_admin/admin_login.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_categories = Category.objects.count()
    total_products = Product.objects.count()
    total_car_brands = CarBrand.objects.count()
    total_car_models = CarModel.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    context = {
        'total_categories': total_categories,
        'total_products': total_products,
        'total_car_brands': total_car_brands,
        'total_car_models': total_car_models,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'custom_admin/dashboard.html', context)


# --- Category Management ---
@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def category_list(request):
    query = request.GET.get('q')
    categories = Category.objects.all().order_by('name_uz')
    if query:
        categories = categories.filter(Q(name_uz__icontains=query) | Q(name_ru__icontains=query))

    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'custom_admin/category_list.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('Kategoriya muvaffaqiyatli qo\'shildi!'))
            return redirect('custom_admin:category_list')
        else:
            messages.error(request,
                           _('Kategoriya qo\'shishda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'title': _('Yangi kategoriya qo\'shish'),
    }
    return render(request, 'custom_admin/category_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('Kategoriya muvaffaqiyatli tahrirlandi!'))
            return redirect('custom_admin:category_list')
        else:
            messages.error(request,
                           _('Kategoriyani tahrirlashda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'title': _('Kategoriyani tahrirlash'),
    }
    return render(request, 'custom_admin/category_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, _('Kategoriya muvaffaqiyatli o\'chirildi!'))
        return redirect('custom_admin:category_list')

    context = {
        'category': category,
    }
    return render(request, 'custom_admin/category_confirm_delete.html', context)


# --- Product Management ---
@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.all().order_by('-created_at')
    if query:
        products = products.filter(
            Q(name_uz__icontains=query) |
            Q(name_ru__icontains=query) |
            Q(description_uz__icontains=query) |
            Q(description_ru__icontains=query)
        )

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'custom_admin/product_list.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def product_create(request):
    ProductImageFormSet = inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=3, can_delete=True)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            messages.success(request, _('Mahsulot muvaffaqiyatli qo\'shildi!'))
            return redirect('custom_admin:product_list')
        else:
            messages.error(request,
                           _('Mahsulot qo\'shishda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': _('Yangi mahsulot qo\'shish'),
    }
    return render(request, 'custom_admin/product_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    ProductImageFormSet = inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=1, can_delete=True)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, _('Mahsulot muvaffaqiyatli tahrirlandi!'))
            return redirect('custom_admin:product_list')
        else:
            messages.error(request,
                           _('Mahsulotni tahrirlashda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    context = {
        'form': form,
        'formset': formset,
        'title': _('Mahsulotni tahrirlash'),
    }
    return render(request, 'custom_admin/product_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, _('Mahsulot muvaffaqiyatli o\'chirildi!'))
        return redirect('custom_admin:product_list')

    context = {
        'product': product,
    }
    return render(request, 'custom_admin/product_confirm_delete.html', context)


# --- Order Management ---
@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def order_list_admin(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    orders = Order.objects.all().order_by('-created_at')

    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(user__username__icontains=query) |
            Q(delivery_address__icontains=query)
        )

    if status_filter and status_filter != 'all':
        orders = orders.filter(status=status_filter)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
    }
    return render(request, 'custom_admin/order_list.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def order_detail_admin(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            old_status = order.status

            order.status = new_status
            order.save()

            if old_status != new_status:
                send_order_status_update(order, new_status)
                messages.success(request, _('Buyurtma holati muvaffaqiyatli yangilandi va mijozga xabar yuborildi!'))
            else:
                messages.info(request, _('Buyurtma holati o\'zgartirilmadi.'))

            return redirect('custom_admin:order_detail', pk=order.pk)
        else:
            messages.error(request, _('Holatni yangilashda xatolik yuz berdi.'))
    else:
        form = OrderStatusForm(initial={'status': order.status})

    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'custom_admin/order_detail.html', context)


# --- CarBrand Management ---
@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def car_brand_list(request):
    query = request.GET.get('q')
    brands = CarBrand.objects.all().order_by('name')
    if query:
        brands = brands.filter(Q(name__icontains=query))

    paginator = Paginator(brands, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'custom_admin/car_brand_list.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def car_brand_create(request):
    if request.method == 'POST':
        form = CarBrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('Avtomobil brendi muvaffaqiyatli qo\'shildi!'))
            return redirect('custom_admin:car_brand_list')
        else:
            messages.error(request,
                           _('Avtomobil brendi qo\'shishda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = CarBrandForm()

    context = {
        'form': form,
        'title': _('Yangi avtomobil brendi qo\'shish'),
    }
    return render(request, 'custom_admin/car_brand_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def car_brand_edit(request, pk):
    brand = get_object_or_404(CarBrand, pk=pk)
    if request.method == 'POST':
        form = CarBrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, _('Avtomobil brendi muvaffaqiyatli tahrirlandi!'))
            return redirect('custom_admin:car_brand_list')
        else:
            messages.error(request,
                           _('Avtomobil brendini tahrirlashda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = CarBrandForm(instance=brand)

    context = {
        'form': form,
        'title': _('Avtomobil brendini tahrirlash'),
    }
    return render(request, 'custom_admin/car_brand_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def car_brand_delete(request, pk):
    brand = get_object_or_404(CarBrand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, _('Avtomobil brendi muvaffaqiyatli o\'chirildi!'))
        return redirect('custom_admin:car_brand_list')

    context = {
        'brand': brand,
    }
    return render(request, 'custom_admin/car_brand_confirm_delete.html', context)


# --- CarModel Management ---
@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def car_model_list(request):
    query = request.GET.get('q')
    models = CarModel.objects.all().order_by('brand__name', 'name')
    if query:
        models = models.filter(Q(name__icontains=query) | Q(brand__name__icontains=query))

    paginator = Paginator(models, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'custom_admin/car_model_list.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def car_model_create(request):
    if request.method == 'POST':
        form = CarModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Avtomobil modeli muvaffaqiyatli qo\'shildi!'))
            return redirect('custom_admin:car_model_list')
        else:
            messages.error(request,
                           _('Avtomobil modeli qo\'shishda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = CarModelForm()

    context = {
        'form': form,
        'title': _('Yangi avtomobil modeli qo\'shish'),
    }
    return render(request, 'custom_admin/car_model_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def car_model_edit(request, pk):
    model = get_object_or_404(CarModel, pk=pk)
    if request.method == 'POST':
        form = CarModelForm(request.POST, instance=model)
        if form.is_valid():
            form.save()
            messages.success(request, _('Avtomobil modeli muvaffaqiyatli tahrirlandi!'))
            return redirect('custom_admin:car_model_list')
        else:
            messages.error(request,
                           _('Avtomobil modelini tahrirlashda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = CarModelForm(instance=model)

    context = {
        'form': form,
        'title': _('Avtomobil modelini tahrirlash'),
    }
    return render(request, 'custom_admin/car_model_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def car_model_delete(request, pk):
    model = get_object_or_404(CarModel, pk=pk)
    if request.method == 'POST':
        model.delete()
        messages.success(request, _('Avtomobil modeli muvaffaqiyatli o\'chirildi!'))
        return redirect('custom_admin:car_model_list')

    context = {
        'model': model,
    }
    return render(request, 'custom_admin/car_model_confirm_delete.html', context)



@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_categories = Category.objects.count()
    total_products = Product.objects.count()
    total_car_brands = CarBrand.objects.count()
    total_car_models = CarModel.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    # Dashboard uchun to'g'ri hisoblash:
    total_payment_cards = PaymentCard.objects.count()
    total_banners = Banner.objects.count()

    context = {
        'total_categories': total_categories,
        'total_products': total_products,
        'total_car_brands': total_car_brands,
        'total_car_models': total_car_models,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_payment_cards': total_payment_cards,
        'total_banners': total_banners,
    }
    return render(request, 'custom_admin/dashboard.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def banner_list(request):
    query = request.GET.get('q')
    banners = Banner.objects.all().order_by('order') # Tartib bo'yicha saralash
    if query:
        banners = banners.filter(
            Q(title_uz__icontains=query) |
            Q(title_ru__icontains=query)
        )

    paginator = Paginator(banners, 10) # Har sahifada 10 ta banner
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'paginator': paginator, # Pagination ma'lumotlari uchun
        'total_banners': banners.count(), # Jami bannerlar soni
    }
    return render(request, 'custom_admin/banner_list.html', context)

@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def banner_create(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('Banner muvaffaqiyatli qo\'shildi!'))
            return redirect('custom_admin:banner_list')
        else:
            messages.error(request,
                           _('Banner qo\'shishda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = BannerForm()

    context = {
        'form': form,
        'title': _('Yangi banner qo\'shish'),
    }
    return render(request, 'custom_admin/banner_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, _('Banner muvaffaqiyatli tahrirlandi!'))
            return redirect('custom_admin:banner_list')
        else:
            messages.error(request,
                           _('Bannerni tahrirlashda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = BannerForm(instance=banner)

    context = {
        'form': form,
        'title': _('Bannerni tahrirlash'),
    }
    return render(request, 'custom_admin/banner_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, _('Banner muvaffaqiyatli o\'chirildi!'))
        return redirect('custom_admin:banner_list')

    context = {
        'banner': banner,
    }
    return render(request, 'custom_admin/banner_confirm_delete.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def payment_card_list(request):
    query = request.GET.get('q')
    payment_cards = PaymentCard.objects.all().order_by('-created_at') # Eng yangilari tepada bo'lsin
    if query:
        payment_cards = payment_cards.filter(
            Q(card_number__icontains=query) |
            Q(card_holder__icontains=query)
        )

    paginator = Paginator(payment_cards, 10) # Har sahifada 10 ta karta
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'paginator': paginator, # Pagination ma'lumotlari uchun
        'total_payment_cards': payment_cards.count(), # Jami to'lov kartalari soni
    }
    return render(request, 'custom_admin/payment_card_list.html', context)

@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def payment_card_create(request):
    if request.method == 'POST':
        form = PaymentCardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('To\'lov kartasi muvaffaqiyatli qo\'shildi!'))
            return redirect('custom_admin:payment_card_list')
        else:
            messages.error(request,
                           _('To\'lov kartasi qo\'shishda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = PaymentCardForm()

    context = {
        'form': form,
        'title': _('Yangi to\'lov kartasi qo\'shish'),
    }
    return render(request, 'custom_admin/payment_card_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def payment_card_edit(request, pk):
    payment_card = get_object_or_404(PaymentCard, pk=pk)
    if request.method == 'POST':
        form = PaymentCardForm(request.POST, instance=payment_card)
        if form.is_valid():
            form.save()
            messages.success(request, _('To\'lov kartasi muvaffaqiyatli tahrirlandi!'))
            return redirect('custom_admin:payment_card_list')
        else:
            messages.error(request,
                           _('To\'lov kartasini tahrirlashda xatolik yuz berdi. Iltimos, formani to\'g\'ri to\'ldiring.'))
    else:
        form = PaymentCardForm(instance=payment_card)

    context = {
        'form': form,
        'title': _('To\'lov kartasini tahrirlash'),
    }
    return render(request, 'custom_admin/payment_card_form.html', context)


@login_required(login_url='custom_admin:admin_login')
@user_passes_test(is_admin)
def payment_card_delete(request, pk):
    payment_card = get_object_or_404(PaymentCard, pk=pk)
    if request.method == 'POST':
        payment_card.delete()
        messages.success(request, _('To\'lov kartasi muvaffaqiyatli o\'chirildi!'))
        return redirect('custom_admin:payment_card_list')

    context = {
        'payment_card': payment_card,
        'title': _('To\'lov kartasini o\'chirishni tasdiqlash'),
    }
    return render(request, 'custom_admin/payment_card_confirm_delete.html', context)