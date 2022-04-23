"""crawler URL Configuration
"""
from django.urls import path
from site_crawler import views as site_crawler_views

urlpatterns = [
    path('', site_crawler_views.CrawlView.as_view()),
]
