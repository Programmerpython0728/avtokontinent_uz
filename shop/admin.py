from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_uz', 'name_ru', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name_uz', 'name_ru']
    prepopulated_fields = {'slug': ('name_uz',)}


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['brand', 'name', 'year_from', 'year_to', 'is_active']
    list_filter = ['brand', 'is_active']
    search_fields = ['name', 'brand__name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name_uz', 'category', 'price_usd', 'get_price_uzs_display', 'is_active', 'is_featured',
                    'views_count']
    list_filter = ['category', 'is_active', 'is_featured', 'is_recommended', 'created_at']
    search_fields = ['name_uz', 'name_ru', 'description_uz']
    prepopulated_fields = {'slug': ('name_uz',)}
    filter_horizontal = ['car_brands', 'car_models']
    inlines = [ProductImageInline]

    def get_price_uzs_display(self, obj):
        return f"{obj.get_price_uzs():,.0f} so'm"

    get_price_uzs_display.short_description = 'Narx (UZS)'


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'is_active', 'created_at']
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = ['user__username', 'product__name_uz', 'comment']
    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)

    approve_comments.short_description = "Izohlarni tasdiqlash"

    def reject_comments(self, request, queryset):
        queryset.update(is_active=False)

    reject_comments.short_description = "Izohlarni rad etish"


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title_uz', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title_uz', 'title_ru']
