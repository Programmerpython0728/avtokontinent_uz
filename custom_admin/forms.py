from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm # AuthenticationForm ni import qilamiz
from shop.models import Category, Product, ProductImage, CarBrand, CarModel, Banner
from orders.models import Order,PaymentCard
from django.utils.translation import gettext_lazy as _


class CustomAdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control w-100'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control w-100'})
    )

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name_uz', 'name_ru', 'slug', 'image', 'parent', 'is_active']
        widgets = {
            'name_uz': forms.TextInput(attrs={'class': 'form-control'}),
            'name_ru': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name_uz': _('Nomi (O\'zbekcha)'),
            'name_ru': _('Nomi (Ruscha)'),
            'slug': _('Slug'),
            'image': _('Rasm'),
            'parent': _('Asosiy kategoriya'),
            'is_active': _('Faol'),
        }

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'name_uz', 'name_ru', 'slug', 'description_uz', 'description_ru',
            'category', 'car_brands', 'car_models', 'price_usd', 'image',
            'video_url', 'is_active', 'is_featured', 'is_recommended'
        ]
        widgets = {
            'name_uz': forms.TextInput(attrs={'class': 'form-control'}),
            'name_ru': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description_uz': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description_ru': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'car_brands': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'car_models': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'price_usd': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name_uz': _('Nomi (O\'zbekcha)'),
            'name_ru': _('Nomi (Ruscha)'),
            'slug': _('Slug'),
            'description_uz': _('Tavsif (O\'zbekcha)'),
            'description_ru': _('Tavsif (Ruscha)'),
            'category': _('Kategoriya'),
            'car_brands': _('Avtomobil brendlari'),
            'car_models': _('Avtomobil modellari'),
            'price_usd': _('Narxi (USD)'),
            'image': _('Asosiy rasm'),
            'video_url': _('Video URL (YouTube)'),
            'is_active': _('Faol'),
            'is_featured': _('Tavsiya qilingan'),
            'is_recommended': _('Eng yaxshi'),
        }

class ProductImageForm(ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'image': _('Rasm'),
            'alt_text': _('Alt matni'),
        }

class OrderStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=Order.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Buyurtma holati')
    )

class CarBrandForm(ModelForm):
    class Meta:
        model = CarBrand
        fields = ['name', 'slug', 'logo', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': _('Nomi'),
            'slug': _('Slug'),
            'logo': _('Logo'),
            'is_active': _('Faol'),
        }

class CarModelForm(ModelForm):
    class Meta:
        model = CarModel
        fields = ['brand', 'name', 'slug', 'year_from', 'year_to', 'is_active']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'year_from': forms.NumberInput(attrs={'class': 'form-control'}),
            'year_to': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'brand': _('Brend'),
            'name': _('Nomi'),
            'slug': _('Slug'),
            'year_from': _('Yildan'),
            'year_to': _('Yilgacha'),
            'is_active': _('Faol'),
        }
class BannerForm(ModelForm):
    class Meta:
        model = Banner
        fields = ['title_uz', 'title_ru', 'image', 'link', 'is_active', 'order']
        widgets = {
            'title_uz': forms.TextInput(attrs={'class': 'form-control'}),
            'title_ru': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title_uz': _('Sarlavha (O\'zbekcha)'),
            'title_ru': _('Sarlavha (Ruscha)'),
            'image': _('Rasm'),
            'link': _('Havola'),
            'is_active': _('Faol'),
            'order': _('Tartib raqami'),
        }

class PaymentCardForm(forms.ModelForm):
    class Meta:
        model = PaymentCard
        fields = ['card_number', 'card_holder', 'is_active']
        widgets = {
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXX XXXX XXXX XXXX'}),
            'card_holder': forms.TextInput(attrs={'class': 'form-control'}),

        }
        labels = {
            'card_number': 'Karta raqami',
            'card_holder': 'Karta egasi',
            'is_active': 'Faol',
        }

