from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
import requests
from .models import Profile
from datetime import timedelta
from django.contrib import messages
from django.conf import settings
import random
import string
from datetime import timedelta, timezone as dt_timezone
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail
from .models import EmailLoginToken
from .forms import UserUpdateForm, ProfileUpdateForm

def login_view(request):
    if request.method == "POST":
        recaptcha_response = request.POST.get("g-recaptcha-response")
        data = {
            "secret": settings.RECAPTCHA_PRIVATE_KEY,
            "response": recaptcha_response
        }

        verify = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data
        )
        result = verify.json()

        if not result.get("success"):
            messages.error(request, "Captcha verification failed. Please try again.")
            return redirect("login")

        # Continue normal logic
        email = request.POST.get("email")
        if email:
            # Send login code logic here
            # send_login_code(email)  # Your email function
            messages.success(request, f"Login code sent to {email}.")
            request.session["email"] = email  # Store for next step
            return redirect("verify_code")  # Next view for code verification
        else:
            messages.error(request, "Email is required.")

    return render(request, "login.html")

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def login_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = generate_code()

        EmailLoginToken.objects.create(email=email, code=code)

        send_mail(
            subject="Your Login Code",
            message=f"Your login code is: {code}",
            from_email="kaustubhpathak9@gmail.com",
            recipient_list=[email],
        )
        request.session["email"] = email
        return redirect("core:verify_code")

    return render(request, "login.html",{
        "recaptcha_site_key": settings.RECAPTCHA_PUBLIC_KEY})

def verify_code(request):
    email = request.session.get("email")
     # ---------- COOLDOWN REMAINING ----------
    cooldown_remaining = 0
    last_sent = request.session.get("last_code_time")

    if last_sent:
        # use datetime.timezone.utc (aliased as dt_timezone)
        last_time = timezone.datetime.fromtimestamp(last_sent, tz=dt_timezone.utc)
        diff = timezone.now() - last_time
        remaining = 60 - diff.total_seconds()
        if remaining > 0:
            cooldown_remaining = int(remaining)

    if request.method == "POST":
        code_entered = request.POST.get("code")
        try:
            token = EmailLoginToken.objects.filter(
                email=email,
                code=code_entered,
                is_used=False,
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).latest("created_at")

            token.is_used = True
            token.save()

            user, created = User.objects.get_or_create(username=email, email=email)

            login(request, user)

            return redirect("core:home")

        except EmailLoginToken.DoesNotExist:
            return render(request, "verify.html", {"error": "Invalid or expired code"})

    return render(request, "verify.html", {
        "error": None,
        "cooldown_remaining": cooldown_remaining
    })

# code for review
def resend_code(request):
    email = request.session.get("email")

    if not email:
        messages.error(request, "Session expired. Please login again.")
        return redirect("login")

    # ---------- RATE LIMIT / COOLDOWN (60 seconds) ----------
    last_sent = request.session.get("last_code_time")
    if last_sent:
        last_time = timezone.datetime.fromtimestamp(last_sent, tz=dt_timezone.utc)
        if timezone.now() - last_time < timedelta(seconds=60):
            messages.error(request, "Please wait before requesting another code.")
            return redirect("core:verify_code")

    # ---------- INVALIDATE OLD UNUSED TOKENS (SECURITY) ----------
    EmailLoginToken.objects.filter(email=email, is_used=False).update(is_used=True)

    # ---------- GENERATE NEW CODE ----------
    code = generate_code()

    EmailLoginToken.objects.create(email=email, code=code)

    send_mail(
        subject="Your Login Code",
        message=f"Your login code is: {code}",
        from_email="kaustubhpathak9@gmail.com",
        recipient_list=[email],
    )

    # ---------- UPDATE RATE LIMIT TIME ----------
    request.session["last_code_time"] = timezone.now().timestamp()

    messages.success(request, "A new verification code has been sent.")
    return redirect("core:verify_code")


@login_required
def home(request):
    return render(request, "index.html")

@login_required
def donate_action(request):
    return render(request, "donate.html")

@login_required
def view_profile(request):
    return render(request, "profile.html")

@login_required
def edit_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("core:view_profile")

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "u_form": u_form,
        "p_form": p_form
    }
    return render(request, "edit_profile.html", context)


def user_logout(request):
    logout(request)
    list(messages.get_messages(request))
    return redirect("core:home")


def home(request):
    return render(request, "index.html")
def about(request):
    return render(request, "about.html")
def trust_members(request):
    return render(request, "trust-members.html")
def how_to_reach(request):
    return render(request, "how-to-reach.html")
def donation_options(request):
    return render(request, "donation.html")
def featured_news(request):
    return render(request, "featured-news.html")
def contact(request):
    return render(request, "contact.html")
def policy(request):
    return render(request, "policy.html")

