from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import *


def home(request):
    try:
        banners = Banner.objects.filter(is_active=True)
        categories = Category.objects.filter(is_active=True, parent=None)
        featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
        recommended_products = Product.objects.filter(is_active=True, is_recommended=True)[:8]

        popular_products = Product.objects.filter(is_active=True).order_by('-views_count')[:8]

        most_liked = Product.objects.filter(is_active=True).annotate(
            likes_count=Count('productlike')
        ).order_by('-likes_count')[:8]

        context = {
            'banners': banners,
            'categories': categories,
            'featured_products': featured_products,
            'recommended_products': recommended_products,
            'popular_products': popular_products,
            'most_liked': most_liked,
        }
    except Exception as e:
        print(f"Database error: {e}")
        context = {
            'banners': [],
            'categories': [],
            'featured_products': [],
            'recommended_products': [],
            'popular_products': [],
            'most_liked': [],
            'error': str(e)
        }

    return render(request, 'shop/home.html', context)


def product_detail(request, slug):
    try:
        product = get_object_or_404(Product, slug=slug, is_active=True)
        product.views_count += 1
        product.save()

        comments = ProductComment.objects.filter(product=product, is_active=True)
        related_products = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(id=product.id)[:4]

        user_liked = False
        user_wishlisted = False
        if request.user.is_authenticated:
            user_liked = ProductLike.objects.filter(user=request.user, product=product).exists()
            user_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()

        context = {
            'product': product,
            'comments': comments,
            'related_products': related_products,
            'user_liked': user_liked,
            'user_wishlisted': user_wishlisted,
        }
        return render(request, 'shop/product_detail.html', context)
    except Exception as e:
        messages.error(request, f'Mahsulot topilmadi: {e}')
        return redirect('shop:home')


def category_detail(request, slug):
    try:
        category = get_object_or_404(Category, slug=slug, is_active=True)
        products = Product.objects.filter(category=category, is_active=True)


        brand_filter = request.GET.get('brand')
        if brand_filter:
            products = products.filter(car_brands__slug=brand_filter)

        sort_by = request.GET.get('sort', 'newest')
        if sort_by == 'price_low':
            products = products.order_by('price_usd')
        elif sort_by == 'price_high':
            products = products.order_by('-price_usd')
        elif sort_by == 'popular':
            products = products.order_by('-views_count')
        else:
            products = products.order_by('-created_at')

        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        car_brands = CarBrand.objects.filter(is_active=True)

        context = {
            'category': category,
            'products': products,
            'car_brands': car_brands,
            'current_brand': brand_filter,
            'current_sort': sort_by,
        }
        return render(request, 'shop/category_detail.html', context)
    except Exception as e:
        messages.error(request, f'Kategoriya topilmadi: {e}')
        return redirect('shop:home')


def car_brand_detail(request, slug):
    try:
        brand = get_object_or_404(CarBrand, slug=slug, is_active=True)
        car_models = CarModel.objects.filter(brand=brand, is_active=True)

        context = {
            'brand': brand,
            'car_models': car_models,
        }
        return render(request, 'shop/car_brand_detail.html', context)
    except Exception as e:
        messages.error(request, f'Brend topilmadi: {e}')
        return redirect('shop:home')


def car_model_parts(request, brand_slug, model_slug):
    try:
        brand = get_object_or_404(CarBrand, slug=brand_slug, is_active=True)
        car_model = get_object_or_404(CarModel, brand=brand, slug=model_slug, is_active=True)
        products = Product.objects.filter(car_models=car_model, is_active=True)

        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        context = {
            'brand': brand,
            'car_model': car_model,
            'products': products,
        }
        return render(request, 'shop/car_model_parts.html', context)
    except Exception as e:
        messages.error(request, f'Model topilmadi: {e}')
        return redirect('shop:home')


def search(request):
    query = request.GET.get('q', '')

    is_featured = request.GET.get('featured') == '1'
    is_popular = request.GET.get('popular') == '1'
    is_most_liked = request.GET.get('most_liked') == '1'  # Yangi filtr

    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name_uz__icontains=query) |
            Q(name_ru__icontains=query) |
            Q(description_uz__icontains=query) |
            Q(description_ru__icontains=query)
        )

    if is_featured:
        products = products.filter(is_featured=True)

    if is_popular:
        products = products.order_by('-views_count')  # Eng ko'p ko'rilganlar

    if is_most_liked:
        products = products.annotate(likes_count=Count('productlike')).order_by(
            '-likes_count')  # Eng ko'p yoqtirilganlar

    if query and not products.exists():
        similar_queries = []
        if 'motor' in query.lower() or 'mator' in query.lower() or 'мотор' in query.lower():
            similar_queries.extend(['motor', 'mator', 'двигатель'])

        for similar_query in similar_queries:
            products = Product.objects.filter(
                Q(name_uz__icontains=similar_query) |
                Q(name_ru__icontains=similar_query) |
                Q(description_uz__icontains=similar_query) |
                Q(description_ru__icontains=similar_query)
            ).filter(is_active=True)
            if products.exists():
                break

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'query': query,
        'is_featured': is_featured,
        'is_popular': is_popular,
        'is_most_liked': is_most_liked,
    }
    return render(request, 'shop/search_results.html', context)


@login_required
def toggle_like(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            like, created = ProductLike.objects.get_or_create(
                user=request.user, product=product
            )
            if not created:
                like.delete()
                liked = False
            else:
                liked = True

            return JsonResponse({
                'liked': liked,
                'likes_count': product.get_likes_count()
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
def toggle_wishlist(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            wishlist, created = Wishlist.objects.get_or_create(
                user=request.user, product=product
            )
            if not created:
                wishlist.delete()
                wishlisted = False
            else:
                wishlisted = True

            return JsonResponse({
                'wishlisted': wishlisted
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
def add_comment(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            comment_text = request.POST.get('comment')
            rating = request.POST.get('rating', 5)

            if comment_text:
                ProductComment.objects.create(
                    user=request.user,
                    product=product,
                    comment=comment_text,
                    rating=int(rating)
                )
                messages.success(request, _('Your comment has been added successfully!'))

            return redirect('shop:product_detail', slug=product.slug)
        except Exception as e:
            messages.error(request, f'Izoh qo\'shishda xatolik: {e}')
            return redirect('shop:home')


@login_required
def wishlist_view(request):
    try:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')

        context = {
            'wishlist_items': wishlist_items,
        }
        return render(request, 'shop/wishlist.html', context)
    except Exception as e:
        messages.error(request, f'Sevimlilar ro\'yxatini yuklashda xatolik: {e}')
        return redirect('shop:home')
