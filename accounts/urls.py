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
    # Password Reset URLs
    path(
        "password-reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # User Dashboard & Profile
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("change-password/", views.change_password, name="change_password"),
    # Wishlist URLs
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views.wishlist_add, name="wishlist_add"),
    path(
        "wishlist/remove/<int:product_id>/",
        views.wishlist_remove,
        name="wishlist_remove",
    ),
    path(
        "wishlist/toggle/<int:product_id>/",
        views.wishlist_toggle,
        name="wishlist_toggle",
    ),
    path(
        "wishlist/toggle/",
        views.toggle_wishlist,
        name="toggle_wishlist",
    ),
    # Admin Dashboard
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    # User Management
    path("admin/users/", views.admin_users_management, name="admin_users_management"),
    path(
        "admin/user/<int:user_id>/", views.admin_user_detail, name="admin_user_detail"
    ),
    path(
        "admin/user/<int:user_id>/toggle/",
        views.admin_toggle_user_status,
        name="admin_toggle_user_status",
    ),
    path(
        "admin/user/<int:user_id>/delete/",
        views.admin_delete_user,
        name="admin_delete_user",
    ),
    # Orders Management
    path(
        "admin/orders/", views.admin_orders_management, name="admin_orders_management"
    ),
    path(
        "admin/order/<str:order_id>/update-status/",
        views.admin_update_order_status,
        name="admin_update_order_status",
    ),
    # Payments Management
    path("admin/payments/", views.admin_payments_list, name="admin_payments_list"),
    path(
        "admin/payment/<int:payment_id>/verify/",
        views.admin_verify_payment,
        name="admin_verify_payment",
    ),
    # Refunds Management
    path(
        "admin/refunds/",
        views.admin_refunds_management,
        name="admin_refunds_management",
    ),
    path(
        "admin/order/<str:order_id>/initiate-refund/",
        views.admin_initiate_refund,
        name="admin_initiate_refund",
    ),
    path(
        "admin/refund/<int:refund_id>/upload-proof/",
        views.admin_upload_refund_proof,
        name="admin_upload_refund_proof",
    ),
    # Complaints Management
    path(
        "admin/complaints/",
        views.admin_complaints_management,
        name="admin_complaints_management",
    ),
    path(
        "admin/complaint/<int:complaint_id>/",
        views.admin_complaint_detail,
        name="admin_complaint_detail",
    ),
    path(
        "admin/complaint-reasons/",
        views.admin_complaint_reasons,
        name="admin_complaint_reasons",
    ),
    path(
        "admin/complaint-reason/<int:reason_id>/toggle/",
        views.admin_toggle_complaint_reason,
        name="admin_toggle_complaint_reason",
    ),
    # Add to urlpatterns list
    # Contact Management
    path("admin/contacts/", views.admin_contacts_list, name="admin_contacts_list"),
    path(
        "admin/contact/<int:contact_id>/reply/",
        views.admin_contact_reply,
        name="admin_contact_reply",
    ),
    path(
        "admin/contact/<int:contact_id>/delete/",
        views.admin_contact_delete,
        name="admin_contact_delete",
    ),
    # Questions Management
    path("admin/questions/", views.admin_questions_list, name="admin_questions_list"),
    path(
        "admin/question/<int:question_id>/reply/",
        views.admin_question_reply,
        name="admin_question_reply",
    ),
    path(
        "admin/question/<int:question_id>/delete/",
        views.admin_question_delete,
        name="admin_question_delete",
    ),
    # Reviews Management
    path("admin/reviews/", views.admin_reviews_list, name="admin_reviews_list"),
    path(
        "admin/review/<int:review_id>/reply/",
        views.admin_review_reply,
        name="admin_review_reply",
    ),
    path(
        "admin/review/<int:review_id>/delete/",
        views.admin_review_delete,
        name="admin_review_delete",
    ),
    # Reports
    path("admin/reports/", views.admin_reports, name="admin_reports"),
]
