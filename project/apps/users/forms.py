
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import UserProfile, Address

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """نموذج تسجيل المستخدم الجديد"""
    email = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'})
    )
    first_name = forms.CharField(
        label='الاسم الأول',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'})
    )
    last_name = forms.CharField(
        label='الاسم الأخير',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأخير'})
    )
    phone = forms.CharField(
        label='رقم الهاتف',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف'})
    )
    password1 = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور'})
    )
    password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تأكيد كلمة المرور'})
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    """نموذج تسجيل الدخول"""
    username = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'})
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور'})
    )


class UserProfileForm(forms.ModelForm):
    """نموذج ملف تعريف المستخدم"""
    first_name = forms.CharField(
        label='الاسم الأول',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='الاسم الأخير',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='رقم الهاتف',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        label='تاريخ الميلاد',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    avatar = forms.ImageField(
        label='الصورة الشخصية',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'website', 'location', 'facebook', 'twitter', 'instagram', 'linkedin',
                  'email_notifications', 'push_notifications', 'sms_notifications']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['birth_date'].initial = self.instance.user.birth_date
            self.fields['avatar'].initial = self.instance.user.avatar

    def save(self, commit=True):
        profile = super().save(commit=False)

        # تحديث بيانات المستخدم
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.birth_date = self.cleaned_data['birth_date']

        if 'avatar' in self.files:
            user.avatar = self.files['avatar']

        if commit:
            user.save()
            profile.save()

        return profile


class AddressForm(forms.ModelForm):
    """نموذج العنوان"""
    class Meta:
        model = Address
        fields = ['type', 'first_name', 'last_name', 'company', 'address_line_1', 'address_line_2',
                  'city', 'state', 'postal_code', 'country', 'phone', 'default']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserPasswordResetForm(PasswordResetForm):
    """نموذج إعادة تعيين كلمة المرور"""
    email = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'})
    )


class UserSetPasswordForm(SetPasswordForm):
    """نموذج تعيين كلمة المرور الجديدة"""
    new_password1 = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور الجديدة'})
    )
    new_password2 = forms.CharField(
        label='تأكيد كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تأكيد كلمة المرور الجديدة'})
    )
