from django.urls import path

from .views import scraping

app_name = 'fpq_scraper'

urlpatterns = [
    path('', scraping, name='scrape'),
]
