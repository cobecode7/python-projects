
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Coupon


class CouponForm(forms.ModelForm):
    """
    نموذج إنشاء وتعديل الكوبونات
    """

    class Meta:
        model = Coupon
        fields = [
            'code', 'name', 'description', 'discount_type', 
            'discount_value', 'minimum_amount', 'maximum_discount',
            'start_date', 'end_date', 'usage_limit', 'is_active',
            'products', 'categories', 'users'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل كود الكوبون')
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('أدخل اسم الكوبون')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('أدخل وصف الكوبون')
            }),
            'discount_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'discount_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'minimum_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'maximum_discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'usage_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'products': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'categories': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'users': forms.SelectMultiple(attrs={
                'class': 'form-select'
            })
        }

    def clean(self):
        """
        التحقق من صحة البيانات
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        discount_type = cleaned_data.get('discount_type')
        discount_value = cleaned_data.get('discount_value')
        maximum_discount = cleaned_data.get('maximum_discount')

        # التحقق من تاريخ البدء والانتهاء
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_('يجب أن يكون تاريخ البدء قبل تاريخ الانتهاء'))

        # التحقق من قيمة الخصم
        if discount_type == 'percentage' and (discount_value < 0 or discount_value > 100):
            raise forms.ValidationError(_('يجب أن تكون نسبة الخصم بين 0 و 100'))

        # التحقق من الحد الأقصى للخصم
        if discount_type == 'percentage' and maximum_discount and maximum_discount < 0:
            raise forms.ValidationError(_('يجب أن يكون الحد الأقصى للخصم قيمة موجبة'))

        return cleaned_data


class ApplyCouponForm(forms.Form):
    """
    نموذج تطبيق الكوبون
    """
    code = forms.CharField(
        label=_('كود الكوبون'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('أدخل كود الكوبون')
        })
    )
