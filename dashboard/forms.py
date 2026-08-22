from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify

from accounts.models import Role
from menus.models import MenuCategory, MenuItem
from orders.models import Order
from orders.services import can_transition_status, transition_order_status
from payments.models import RestaurantPaymentConfig
from restaurants.models import DiningTable, MenuAppearanceTheme, Restaurant


class EmployeeCreateForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=6,
        label='Password',
    )
    role = forms.ChoiceField(
        choices=[
            (Role.ADMIN, 'Admin'),
            (Role.KASIR, 'Kasir'),
            (Role.DAPUR, 'Dapur'),
        ],
        label='Peran',
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email sudah digunakan.')
        return email


class EmployeeUpdateForm(forms.Form):
    role = forms.ChoiceField(
        choices=[
            (Role.ADMIN, 'Admin'),
            (Role.KASIR, 'Kasir'),
            (Role.DAPUR, 'Dapur'),
        ],
        label='Peran',
    )
    is_active = forms.BooleanField(required=False, label='Aktif')


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            'name',
            'slug',
            'description',
            'address',
            'phone',
            'logo',
            'is_active',
        ]


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
            'banner_image',
            'tagline',
            'greeting_message',
            'receipt_footer_text',
            'contact_phone',
            'contact_instagram',
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
            'show_category_tabs': forms.CheckboxInput(
                attrs={'class': 'theme-checkbox'}
            ),
            'banner_image': forms.ClearableFileInput(attrs={'class': 'theme-input'}),
            'tagline': forms.TextInput(
                attrs={
                    'class': 'theme-input',
                    'placeholder': 'Contoh: Jagonya Ayam Geprek',
                },
            ),
            'greeting_message': forms.TextInput(
                attrs={
                    'class': 'theme-input',
                    'placeholder': 'Contoh: Selamat datang di Warung Bu Dewi 👋',
                },
            ),
            'receipt_footer_text': forms.TextInput(
                attrs={
                    'class': 'theme-input',
                    'placeholder': 'Terima kasih atas kunjungan Anda',
                },
            ),
            'contact_phone': forms.TextInput(
                attrs={
                    'class': 'theme-input',
                    'placeholder': '0812xxxx',
                },
            ),
            'contact_instagram': forms.TextInput(
                attrs={
                    'class': 'theme-input',
                    'placeholder': 'username_tanpa_at',
                },
            ),
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
        base_slug = slugify(slug or name) or 'kategori'
        restaurant = self.cleaned_data.get('restaurant')

        if not restaurant:
            return base_slug

        unique_slug = base_slug
        counter = 1
        qs = MenuCategory.objects.filter(restaurant=restaurant)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        while qs.filter(slug=unique_slug).exists():
            unique_slug = f'{base_slug}-{counter}'
            counter += 1

        return unique_slug


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
            'restaurant': forms.Select(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl px-4 py-3 focus:outline-none '
                        'focus:border-primary focus:ring-1 '
                        'focus:ring-primary text-sm font-medium'
                    ),
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl px-4 py-3 focus:outline-none '
                        'focus:border-primary focus:ring-1 '
                        'focus:ring-primary text-sm font-medium'
                    ),
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl px-4 py-3 focus:outline-none '
                        'focus:border-primary focus:ring-1 '
                        'focus:ring-primary text-sm font-medium'
                    ),
                    'placeholder': 'Contoh: Ayam Geprek',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl px-4 py-3 focus:outline-none '
                        'focus:border-primary focus:ring-1 '
                        'focus:ring-primary text-sm font-medium '
                        'resize-none'
                    ),
                    'rows': 3,
                    'placeholder': 'Jelaskan bahan utama atau rasa...',
                }
            ),
            'price': forms.NumberInput(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl pl-10 pr-4 py-3 focus:outline-none '
                        'focus:border-primary focus:ring-1 '
                        'focus:ring-primary text-lg font-bold text-dark'
                    ),
                    'placeholder': '0',
                }
            ),
            'discount': forms.NumberInput(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl px-4 py-2.5 focus:outline-none '
                        'focus:border-primary focus:ring-1 '
                        'focus:ring-primary text-sm font-medium'
                    ),
                    'placeholder': '0',
                    'min': 0,
                    'max': 100,
                }
            ),
            'tax': forms.NumberInput(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl px-4 py-2.5 focus:outline-none '
                        'focus:border-primary focus:ring-1 '
                        'focus:ring-primary text-sm font-medium'
                    ),
                    'placeholder': '10',
                    'min': 0,
                    'max': 100,
                }
            ),
            'stock': forms.NumberInput(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl px-4 py-2.5 focus:outline-none '
                        'focus:border-primary text-sm font-medium'
                    ),
                    'placeholder': '0',
                }
            ),
            'sort_order': forms.NumberInput(
                attrs={
                    'class': (
                        'w-full bg-gray-50 border border-gray-200 '
                        'rounded-xl px-4 py-3 focus:outline-none '
                        'focus:border-primary focus:ring-1 '
                        'focus:ring-primary text-sm font-medium'
                    ),
                }
            ),
            'is_available': forms.CheckboxInput(
                attrs={
                    'class': (
                        'toggle-checkbox absolute block w-5 h-5 '
                        'rounded-full bg-white border-4 appearance-none '
                        'cursor-pointer transition-all duration-300 left-0 '
                        'border-gray-300'
                    ),
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': (
                        'toggle-checkbox absolute block w-5 h-5 '
                        'rounded-full bg-white border-4 appearance-none '
                        'cursor-pointer transition-all duration-300 left-0 '
                        'border-gray-300'
                    ),
                    'checked': True,
                }
            ),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name', '')
        base_slug = slugify(slug or name) or 'menu'
        restaurant = self.cleaned_data.get('restaurant')

        if not restaurant:
            return base_slug

        unique_slug = base_slug
        counter = 1
        qs = MenuItem.objects.filter(restaurant=restaurant)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        while qs.filter(slug=unique_slug).exists():
            unique_slug = f'{base_slug}-{counter}'
            counter += 1

        return unique_slug


class RestaurantPaymentConfigForm(forms.ModelForm):
    # Plain text inputs - will be encrypted on save. Empty = keep existing.
    midtrans_server_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm',
                'placeholder': 'SB-Mid-server-xxxx',
                'autocomplete': 'off',
            },
            render_value=False,
        ),
        label='Midtrans Server Key',
        help_text='Dari dashboard.midtrans.com — jangan bagikan.',
    )
    midtrans_client_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm',
                'placeholder': 'SB-Mid-client-xxxx',
                'autocomplete': 'off',
            },
            render_value=False,
        ),
        label='Midtrans Client Key',
    )

    class Meta:
        model = RestaurantPaymentConfig
        fields = ['gateway', 'midtrans_is_production', 'is_active']
        widgets = {
            'gateway': forms.Select(
                attrs={
                    'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-medium',
                }
            ),
            'midtrans_is_production': forms.CheckboxInput(attrs={'class': 'w-4 h-4'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4'}),
        }

    def clean(self):
        cleaned = super().clean()
        gateway = cleaned.get('gateway')
        server_key = (
            self.data.get('midtrans_server_key', '').strip()
            if hasattr(self, 'data')
            else ''
        )
        client_key = (
            self.data.get('midtrans_client_key', '').strip()
            if hasattr(self, 'data')
            else ''
        )
        # Also check existing encrypted values when editing
        has_existing_server = bool(self.instance and self.instance.midtrans_server_key)
        has_existing_client = bool(self.instance and self.instance.midtrans_client_key)
        has_server = bool(server_key) or has_existing_server
        has_client = bool(client_key) or has_existing_client
        if gateway == RestaurantPaymentConfig.Gateway.MIDTRANS:
            if not has_server or not has_client:
                raise forms.ValidationError(
                    'Untuk Midtrans, Server Key dan Client Key wajib diisi.'
                )
        return cleaned


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(
                attrs={
                    'class': 'w-full bg-white border-2 border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-dark focus:border-primary focus:ring-4 focus:ring-secondary/40 outline-none transition-all',
                }
            ),
        }

    def clean_status(self):
        new_status = self.cleaned_data['status']
        instance = self.instance
        if instance and instance.pk:
            # NOTE: construct_instance() may already have mutated instance.status,
            # so always validate against the persisted DB value.
            persisted_status = (
                Order.objects.filter(pk=instance.pk)
                .values_list(
                    'status',
                    flat=True,
                )
                .first()
            )
            current_status = persisted_status or instance.status
            if not can_transition_status(current_status, new_status):
                cur_label = dict(Order.Status.choices).get(
                    current_status, current_status
                )
                new_label = dict(Order.Status.choices).get(new_status, new_status)
                raise forms.ValidationError(
                    f'Tidak bisa mengubah status dari "{cur_label}" ke "{new_label}".',
                )
        return new_status

    def save(self, commit=True):
        order = self.instance
        new_status = self.cleaned_data['status']
        if not commit:
            # Return the instance with the pending status applied, but do not
            # persist (used when the caller wants to inspect first).
            order.status = new_status
            return order
        # Re-fetch the persisted status because construct_instance() may have
        # mutated order.status before save() is called.
        if order.pk:
            persisted_status = (
                Order.objects.filter(pk=order.pk)
                .values_list(
                    'status',
                    flat=True,
                )
                .first()
            )
            if persisted_status and persisted_status != order.status:
                order.status = persisted_status
        return transition_order_status(order=order, new_status=new_status)
