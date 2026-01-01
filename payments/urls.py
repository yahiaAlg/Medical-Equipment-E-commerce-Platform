from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("update-cart/", views.update_cart, name="update_cart"),
    path(
        "remove-from-cart/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path("checkout/", views.checkout, name="checkout"),
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoice/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path(
        "invoice/<int:invoice_id>/upload-proof/",
        views.upload_payment_proof,
        name="upload_payment_proof",
    ),
    path(
        "invoice/<int:invoice_id>/receipt/",
        views.payment_receipt,
        name="payment_receipt",
    ),
    # Complaints
    path(
        "order/<int:order_id>/complaint/",
        views.complaint_create,
        name="complaint_create",
    ),
    path("complaints/", views.complaint_list, name="complaint_list"),
    path(
        "complaint/<int:complaint_id>/", views.complaint_detail, name="complaint_detail"
    ),
    # Refund Receipt
    path(
        "refund/<int:refund_id>/receipt/", views.refund_receipt, name="refund_receipt"
    ),
    # Notifications
    path(
        "notification/<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),
    path(
        "notifications/mark-all-read/",
        views.mark_all_notifications_read,
        name="mark_all_notifications_read",
    ),
]
