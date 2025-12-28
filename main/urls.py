from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "core"  # enables namespacing

urlpatterns = [
    path('', views.home, name="home"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("donate/", views.donate_action, name="donate"),
    path("profile/", views.view_profile, name="view_profile"),
    path("policy/",views.policy,name="policy"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("verify/", views.verify_code, name="verify_code"),
    path("home/", views.home, name="home"),
    path('about/', views.about, name="about"),
    path('trust-members/', views.trust_members, name="trust-members"),
    path('how-to-reach/', views.how_to_reach, name="how-to-reach"),
    path('donation-options/', views.donation_options, name="donation-options"),
    path('featured-news/', views.featured_news, name="featured-news"),
    path('contact-us/', views.contact, name="contact"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
