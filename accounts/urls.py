from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # User Dashboard & Profile
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path(
        "wishlist/remove/<int:product_id>/",
        views.wishlist_remove,
        name="wishlist_remove",
    ),
    # Admin Dashboard
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", views.admin_users, name="admin_users"),
    path(
        "admin/users/toggle/<int:user_id>/",
        views.admin_toggle_user,
        name="admin_toggle_user",
    ),
    path(
        "admin/products-report/",
        views.admin_products_report,
        name="admin_products_report",
    ),
    path("admin/stats-api/", views.admin_stats_api, name="admin_stats_api"),
]
