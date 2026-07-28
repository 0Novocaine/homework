from django.contrib.auth.views import LoginView
from django.urls import path

from .forms import LoginForm
from .views import RegisterView, signout

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
]
