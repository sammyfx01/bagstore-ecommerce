from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
]