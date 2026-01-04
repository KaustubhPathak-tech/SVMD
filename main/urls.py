from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "core"  # enables namespacing

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('trust-members/', views.trust_members, name="trust-members"),
    path('how-to-reach/', views.how_to_reach, name="how-to-reach"),
    path('donation-options/', views.donation_options, name="donation-options"),
    path('featured-news/', views.featured_news, name="featured-news"),
    path('contact-us/', views.contact, name="contact"),
    path("policy/",views.policy,name="policy"),
    
    path("donation-receipt/", views.donate_action, name="donation-receipt"),
    path("receipt/<int:pk>/pdf/", views.download_receipt_pdf, name="download_receipt_pdf"),

    
    path("login/", views.login_request, name="login"),
    path("verify/", views.verify_code, name="verify_code"),
    path("resend-code/", views.resend_code, name="resend_code"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.view_profile, name="view_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    
    path("staff/",views.staff_dashboard,name="staff-dashboard"),
    path("staff/receipts/", views.admin_receipt_list, name="admin-receipt-list"),
    path("staff/receipts/<int:pk>/", views.update_receipt_status, name="admin-receipt-detail"),
    path("staff/transactions/",views.admin_transaction_list,name="admin-transaction-list"),

   
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
