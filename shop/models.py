from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from shop.services.currency import  get_usd_to_uzs_rate


class CurrencyRate(models.Model):
    usd_to_uzs = models.DecimalField(max_digits=10, decimal_places=2, default=12500)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Currency Rate')
        verbose_name_plural = _('Currency Rates')


class Category(models.Model):
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_uz

    def get_absolute_url(self):
        return reverse('shop:category_detail', args=[self.slug])

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class CarBrand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='car_brands/', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Car Brand')
        verbose_name_plural = _('Car Brands')


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    year_from = models.IntegerField(null=True, blank=True)
    year_to = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    class Meta:
        verbose_name = _('Car Model')
        verbose_name_plural = _('Car Models')
        unique_together = ['brand', 'slug']


class Product(models.Model):
    name_uz = models.CharField(max_length=300)
    name_ru = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    description_uz = models.TextField()
    description_ru = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    car_brands = models.ManyToManyField(CarBrand, blank=True)
    car_models = models.ManyToManyField(CarModel, blank=True)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    video_url = models.URLField(blank=True, help_text="YouTube video URL")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_uz

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def get_price_uzs(self):
        rate = CurrencyRate.objects.first()
        if rate:
            usd_to_uzs = rate.usd_to_uzs
        else:
            usd_to_uzs = get_usd_to_uzs_rate()  # Bu ham Decimal bo‘lsin!

        return self.price_usd * usd_to_uzs
    def get_comments_count(self):
        return self.productcomment_set.filter(is_active=True).count()

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')


class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        verbose_name = _('Product Like')
        verbose_name_plural = _('Product Likes')


class ProductComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    is_active = models.BooleanField(default=True)
    admin_reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Product Comment')
        verbose_name_plural = _('Product Comments')
        ordering = ['-created_at']


class Banner(models.Model):
    title_uz = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['order']


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')
