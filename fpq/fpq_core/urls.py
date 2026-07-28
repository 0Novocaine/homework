from django.urls import path

from .views import index

app_name = 'fpq_core'

urlpatterns = [
    path('', index, name='index'),
]
