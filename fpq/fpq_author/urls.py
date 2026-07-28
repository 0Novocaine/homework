from django.urls import path

from .views import CreationView, detail

app_name = 'fpq_author'

urlpatterns = [
    path('', CreationView.as_view(), name='create'),
    path('<int:author_id>/', detail, name='detail'),
]
