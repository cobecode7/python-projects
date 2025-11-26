
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import User, Address, UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, AddressSerializer,
    RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    ResetPasswordSerializer, ConfirmResetPasswordSerializer
)
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm,
    UserPasswordResetForm, UserSetPasswordForm
)


# API Views
class RegisterView(generics.CreateAPIView):
    """تسجيل مستخدم جديد"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # إرسال بريد تأكيد
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirmation_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"

        send_mail(
            subject='تأكيد البريد الإلكتروني',
            message=f'يرجى تأكيد بريدك الإلكتروني عبر الرابط التالي: {confirmation_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {'message': 'تم إنشاء الحساب بنجاح. يرجى تأكيد بريدك الإلكتروني.'},
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    """تسجيل الدخول"""
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_verified:
                return Response(
                    {'error': 'يرجى تأكيد بريدك الإلكتروني أولاً'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })

        return Response(
            {'error': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """تسجيل الخروج"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'تم تسجيل الخروج بنجاح'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshTokenView(TokenRefreshView):
    """تجديد رمز الوصول"""
    pass


class ChangePasswordView(generics.UpdateAPIView):
    """تغيير كلمة المرور"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'تم تغيير كلمة المرور بنجاح'})


class ResetPasswordView(generics.GenericAPIView):
    """طلب إعادة تعيين كلمة المرور"""
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

            send_mail(
                subject='إعادة تعيين كلمة المرور',
                message=f'يرجى إعادة تعيين كلمة المرور عبر الرابط التالي: {reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response(
            {'message': 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني'}
        )


class ConfirmResetPasswordView(generics.GenericAPIView):
    """تأكيد إعادة تعيين كلمة المرور"""
    serializer_class = ConfirmResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'تم إعادة تعيين كلمة المرور بنجاح'})
            else:
                return Response(
                    {'error': 'رابط غير صالح أو منتهي الصلاحية'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'رابط غير صالح'},
                status=status.HTTP_400_BAD_REQUEST
            )


class VerifyEmailView(generics.GenericAPIView):
    """تأكيد البريد الإلكتروني"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, uid, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if default_token_generator.check_token(user, token):
                user.is_verified = True
                user.save()
                return Response({'message': 'تم تأكيد بريدك الإلكتروني بنجاح'})
            else:
                return Response(
                    {'error': 'رابط التأكيد غير صالح أو منتهي الصلاحية'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'رابط التأكيد غير صالح'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """عرض وتحديث ملف تعريف المستخدم"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class UserProfileViewSet(viewsets.ModelViewSet):
    """مجموعة طلبات لعرض وتعديل ملفات تعريف المستخدمين"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)


class AddressViewSet(viewsets.ModelViewSet):
    """عرض وتعديل عناوين المستخدم"""
    queryset = Address.objects.all()  # Default queryset required by router
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # إذا كان هذا هو العنوان الأول أو تم تحديده كعنوان افتراضي
        if serializer.validated_data.get('default', False) or not Address.objects.filter(user=self.request.user).exists():
            # إلغاء تحديد جميع العناوين الافتراضية الأخرى
            Address.objects.filter(user=self.request.user, default=True).update(default=False)
            serializer.save(user=self.request.user, default=True)
        else:
            serializer.save(user=self.request.user)


class DefaultAddressView(generics.UpdateAPIView):
    """تعيين العنوان الافتراضي"""
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        address_id = request.data.get('address_id')

        if not address_id:
            return Response(
                {'error': 'يجب تحديد معرف العنوان'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            address = Address.objects.get(id=address_id, user=request.user)

            # إلغاء تحديد جميع العناوين الافتراضية الأخرى
            Address.objects.filter(user=request.user, default=True).update(default=False)

            # تعيين العنوان الحالي كعنوان افتراضي
            address.default = True
            address.save()

            return Response({'message': 'تم تعيين العنوان الافتراضي بنجاح'})
        except Address.DoesNotExist:
            return Response(
                {'error': 'العنوان غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )


# Frontend Views
class LoginViewFrontend(TemplateView):
    """صفحة تسجيل الدخول"""
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserLoginForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_verified:
                    login(request, user)
                    next_url = request.GET.get('next', reverse_lazy('home'))
                    return redirect(next_url)
                else:
                    messages.error(request, 'يرجى تأكيد بريدك الإلكتروني أولاً')
            else:
                messages.error(request, 'البريد الإلكتروني أو كلمة المرور غير صحيحة')

        return self.render_to_response({'form': form})


class RegisterViewFrontend(CreateView):
    """صفحة تسجيل مستخدم جديد"""
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login_frontend')

    def form_valid(self, form):
        response = super().form_valid(form)

        # إرسال بريد تأكيد
        user = form.instance
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirmation_link = f"{self.request.build_absolute_uri('/')}verify-email/{uid}/{token}/"

        send_mail(
            subject='تأكيد البريد الإلكتروني',
            message=f'يرجى تأكيد بريدك الإلكتروني عبر الرابط التالي: {confirmation_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'تم إنشاء الحساب بنجاح. يرجى تأكيد بريدك الإلكتروني.')
        return response


@method_decorator(csrf_protect, name='dispatch')
class VerifyEmailViewFrontend(TemplateView):
    """صفحة تأكيد البريد الإلكتروني"""
    template_name = 'users/verify_email.html'

    def get(self, request, uid, token, *args, **kwargs):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if default_token_generator.check_token(user, token):
                user.is_verified = True
                user.save()
                messages.success(request, 'تم تأكيد بريدك الإلكتروني بنجاح. يمكنك الآن تسجيل الدخول.')
                return redirect('login_frontend')
            else:
                messages.error(request, 'رابط التأكيد غير صالح أو منتهي الصلاحية')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'رابط التأكيد غير صالح')

        return super().get(request, *args, **kwargs)


class ProfileViewFrontend(LoginRequiredMixin, DetailView):
    """صفحة الملف الشخصي"""
    template_name = 'users/profile.html'
    login_url = 'login_frontend'

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class EditProfileViewFrontend(LoginRequiredMixin, UpdateView):
    """صفحة تعديل الملف الشخصي"""
    template_name = 'users/edit_profile.html'
    form_class = UserProfileForm
    login_url = 'login_frontend'
    success_url = reverse_lazy('profile_frontend')

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث ملفك الشخصي بنجاح')
        return super().form_valid(form)


class PasswordResetViewFrontend(TemplateView):
    """صفحة طلب إعادة تعيين كلمة المرور"""
    template_name = 'users/password_reset.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserPasswordResetForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(f'/reset/{uid}/{token}/')

                send_mail(
                    subject='إعادة تعيين كلمة المرور',
                    message=f'يرجى إعادة تعيين كلمة المرور عبر الرابط التالي: {reset_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            messages.success(request, 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني')
            return redirect('password_reset_done_frontend')

        return self.render_to_response({'form': form})


@method_decorator(csrf_protect, name='dispatch')
class PasswordResetConfirmViewFrontend(TemplateView):
    """صفحة تأكيد إعادة تعيين كلمة المرور"""
    template_name = 'users/password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserSetPasswordForm()
        return context

    def get(self, request, uid, token, *args, **kwargs):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if not default_token_generator.check_token(user, token):
                messages.error(request, 'رابط إعادة التعيين غير صالح أو منتهي الصلاحية')
                return redirect('password_reset_frontend')

            request.session['reset_user_id'] = user_id
            return super().get(request, *args, **kwargs)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'رابط إعادة التعيين غير صالح')
            return redirect('password_reset_frontend')

    def post(self, request, *args, **kwargs):
        form = UserSetPasswordForm(request.POST)

        if form.is_valid():
            user_id = request.session.get('reset_user_id')

            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    user.set_password(form.cleaned_data['new_password'])
                    user.save()

                    del request.session['reset_user_id']
                    messages.success(request, 'تم إعادة تعيين كلمة المرور بنجاح')
                    return redirect('login_frontend')
                except User.DoesNotExist:
                    messages.error(request, 'حدث خطأ ما')

        return self.render_to_response({'form': form})


class AddressesViewFrontend(LoginRequiredMixin, ListView):
    """صفحة عرض العناوين"""
    template_name = 'users/addresses.html'
    model = Address
    context_object_name = 'addresses'
    login_url = 'login_frontend'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddAddressViewFrontend(LoginRequiredMixin, CreateView):
    """صفحة إضافة عنوان جديد"""
    template_name = 'users/add_address.html'
    form_class = AddressForm
    model = Address
    login_url = 'login_frontend'
    success_url = reverse_lazy('addresses_frontend')

    def form_valid(self, form):
        form.instance.user = self.request.user

        # إذا كان هذا هو العنوان الأول أو تم تحديده كعنوان افتراضي
        if form.cleaned_data.get('default', False) or not Address.objects.filter(user=self.request.user).exists():
            # إلغاء تحديد جميع العناوين الافتراضية الأخرى
            Address.objects.filter(user=self.request.user, default=True).update(default=False)
            form.instance.default = True

        messages.success(self.request, 'تم إضافة العنوان بنجاح')
        return super().form_valid(form)


class EditAddressViewFrontend(LoginRequiredMixin, UpdateView):
    """صفحة تعديل العنوان"""
    template_name = 'users/edit_address.html'
    form_class = AddressForm
    model = Address
    login_url = 'login_frontend'
    success_url = reverse_lazy('addresses_frontend')

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # إذا تم تحديد العنوان الحالي كعنوان افتراضي
        if form.cleaned_data.get('default', False):
            # إلغاء تحديد جميع العناوين الافتراضية الأخرى
            Address.objects.filter(user=self.request.user, default=True).update(default=False)
            form.instance.default = True

        messages.success(self.request, 'تم تحديث العنوان بنجاح')
        return super().form_valid(form)


class DeleteAddressViewFrontend(LoginRequiredMixin, DeleteView):
    """صفحة حذف العنوان"""
    model = Address
    login_url = 'login_frontend'
    success_url = reverse_lazy('addresses_frontend')

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف العنوان بنجاح')
        return super().delete(request, *args, **kwargs)


class SettingsViewFrontend(LoginRequiredMixin, TemplateView):
    """صفحة الإعدادات"""
    template_name = 'users/settings.html'
    login_url = 'login_frontend'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context

    def post(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # تحديث إعدادات الإشعارات
        profile.email_notifications = request.POST.get('email_notifications', 'off') == 'on'
        profile.push_notifications = request.POST.get('push_notifications', 'off') == 'on'
        profile.sms_notifications = request.POST.get('sms_notifications', 'off') == 'on'
        profile.save()

        messages.success(request, 'تم تحديث الإعدادات بنجاح')
        return redirect('settings_frontend')
