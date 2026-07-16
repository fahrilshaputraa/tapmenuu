from django import forms
from django.utils.text import slugify

from menus.models import MenuCategory, MenuItem
from orders.models import Order
from restaurants.models import DiningTable, MenuAppearanceTheme, Restaurant


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'slug', 'description', 'address', 'phone', 'is_active']


class MenuAppearanceThemeForm(forms.ModelForm):
    COLOR_FIELDS = [
        'primary_color',
        'secondary_color',
        'accent_color',
        'background_color',
        'text_color',
        'card_color',
    ]

    class Meta:
        model = MenuAppearanceTheme
        fields = [
            'primary_color',
            'secondary_color',
            'accent_color',
            'background_color',
            'text_color',
            'card_color',
            'font_family',
            'layout_style',
            'header_style',
            'button_style',
            'show_category_tabs',
        ]
        widgets = {
            'font_family': forms.Select(
                choices=[
                    ('Plus Jakarta Sans', 'Plus Jakarta Sans'),
                    ('Inter', 'Inter'),
                    ('Poppins', 'Poppins'),
                    ('Nunito', 'Nunito'),
                    ('Lora', 'Lora'),
                ],
                attrs={'class': 'theme-input'},
            ),
            'layout_style': forms.Select(attrs={'class': 'theme-input'}),
            'header_style': forms.Select(attrs={'class': 'theme-input'}),
            'button_style': forms.Select(attrs={'class': 'theme-input'}),
            'show_category_tabs': forms.CheckboxInput(attrs={'class': 'theme-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.COLOR_FIELDS:
            self.fields[field_name].widget = forms.TextInput(
                attrs={
                    'type': 'color',
                    'class': 'theme-color-input',
                    'data-theme-field': field_name,
                },
            )


class DiningTableForm(forms.ModelForm):
    class Meta:
        model = DiningTable
        fields = ['restaurant', 'table_number', 'capacity', 'is_active']


class MenuCategoryForm(forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = MenuCategory
        fields = ['restaurant', 'name', 'slug', 'sort_order', 'is_active']

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name', '')
        return slugify(slug or name) or 'kategori'


class MenuItemForm(forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = MenuItem
        fields = [
            'restaurant',
            'category',
            'name',
            'slug',
            'description',
            'price',
            'discount',
            'tax',
            'stock',
            'image',
            'is_available',
            'is_active',
            'is_favorite',
            'is_new',
            'sort_order',
        ]
        widgets = {
            'restaurant': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm font-medium',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm font-medium',
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm font-medium',
                'placeholder': 'Contoh: Ayam Geprek',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm font-medium resize-none',
                'rows': 3,
                'placeholder': 'Jelaskan bahan utama atau rasa...',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl pl-10 pr-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-lg font-bold text-dark',
                'placeholder': '0',
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm font-medium',
                'placeholder': '0',
                'min': 0,
                'max': 100,
            }),
            'tax': forms.NumberInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm font-medium',
                'placeholder': '10',
                'min': 0,
                'max': 100,
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:border-primary text-sm font-medium',
                'placeholder': '0',
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm font-medium',
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer transition-all duration-300 left-0 border-gray-300',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer transition-all duration-300 left-0 border-gray-300',
                'checked': True,
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name', '')
        return slugify(slug or name) or 'menu'


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
