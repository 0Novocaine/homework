from django.urls import path

from .views import CreationView

app_name = 'fpq_quote'

urlpatterns = [
    path('', CreationView.as_view(), name='create'),
]
