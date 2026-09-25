from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
)
from django.urls import path, reverse_lazy

from .forms import LoginForm
from .views import RegisterView, ResetPasswordView, signout

app_name = 'fpq_user'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
            template_name='fpq_user/login.html',
            form_class=LoginForm,
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path('logout/', signout, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('reset-password/', ResetPasswordView.as_view(), name='password_reset'),
    path(
        'reset-password/done/',
        PasswordResetDoneView.as_view(
            template_name='fpq_user/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset-password/confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='fpq_user/password_reset_confirm.html',
            success_url=reverse_lazy('fpq_user:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset-password/complete/',
        PasswordResetCompleteView.as_view(
            template_name='fpq_user/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
