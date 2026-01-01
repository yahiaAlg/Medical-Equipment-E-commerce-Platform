from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("specialties/", views.specialty_list, name="specialties"),  # ADD THIS
    path("search/", views.search, name="search"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("product/<slug:slug>/", views.product_detail, name="detail"),
    path("toggle-wishlist/", views.toggle_wishlist, name="toggle_wishlist"),
    path("add-review/", views.add_review, name="add_review"),
    path("ask-question/", views.ask_question, name="ask_question"),
]
