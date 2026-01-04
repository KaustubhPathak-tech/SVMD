from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.db import transaction
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
from .utils import generate_receipt_pdf
from django.shortcuts import render, redirect,get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail,EmailMessage
from .models import EmailLoginToken, DonationReceiptRequest, Transaction,Address
from .forms import UserUpdateForm, ProfileUpdateForm, DonationReceiptForm,AddressUpdateForm

from django.views.decorators.cache import cache_page

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def login_request(request):
    if request.method == "POST":
        # ---- reCAPTCHA verification ----
        recaptcha_response = request.POST.get("g-recaptcha-response")
        verify = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.RECAPTCHA_PRIVATE_KEY,
                "response": recaptcha_response
            }
        )
        result = verify.json()

        if not result.get("success"):
            messages.error(request, "Captcha verification failed.")
            return redirect("core:login")

        # ---- Email + OTP ----
        email = request.POST.get("email")
        if not email:
            messages.error(request, "Email is required.")
            return redirect("core:login")

        code = generate_code()

        EmailLoginToken.objects.create(email=email, code=code)

        send_mail(
            subject="Your Login Code",
            message=f"Your login code is: {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        request.session["email"] = email
        messages.success(request, "Login code sent to your email.")

        return redirect("core:verify_code")

    return render(request, "login.html", {
        "recaptcha_site_key": settings.RECAPTCHA_PUBLIC_KEY
    })

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
def donate_action(request):
    profile = request.user.profile  # assumes Profile is created at signup
    show_history = False
    
    if request.method == "POST":
        form = DonationReceiptForm(request.POST)

        if form.is_valid():
            receipt_request = form.save(commit=False)
            receipt_request.profile = profile
            receipt_request.status = "PENDING"   #to change later "PENDING"
            receipt_request.save()

            messages.success(
                request,
                "Your receipt request has been submitted successfully and is under verification."
            )
            show_history = True
            form = DonationReceiptForm()   # redirect to same page or status page

        else:
            messages.error(
                request,
                "Please correct the highlighted errors and submit again."
            )

    else:
        form = DonationReceiptForm()
        if request.GET.get("view") == "history":
            show_history = True
            
            
    receipt_history = DonationReceiptRequest.objects.filter(
        profile=profile
    ).order_by("-created_at")
    return render(
        request,
        "donate.html",
        {
            "form": form,
            "receipt_history": receipt_history,
            "show_history": show_history,
        }
    )

@login_required
def receipt_request_history(request):
    requests = DonationReceiptRequest.objects.filter(
        profile=request.user.profile
    ).order_by("-created_at")

    return render(
        request,
        "receipt_history.html",
        {"requests": requests}
    )

@login_required
def view_profile(request):
    return render(request, "profile.html")

@login_required
# def edit_profile(request):
#     if request.method == "POST":
#         u_form = UserUpdateForm(request.POST, instance=request.user)
#         p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

#         if u_form.is_valid() and p_form.is_valid():
#             u_form.save()
#             p_form.save()
#             return redirect("core:view_profile")

#     else:
#         u_form = UserUpdateForm(instance=request.user)
#         p_form = ProfileUpdateForm(instance=request.user.profile)

#     context = {
#         "u_form": u_form,
#         "p_form": p_form
#     }
#     return render(request, "edit_profile.html", context)

@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    # 🔹 ADDED: Safe address retrieval
    address, created = Address.objects.get_or_create(profile=profile)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        a_form = AddressUpdateForm(request.POST, instance=address)  # 🔹 ADDED

        if u_form.is_valid() and p_form.is_valid() and a_form.is_valid():
            u_form.save()
            p_form.save()
            a_form.save()  # 🔹 ADDED
            return redirect("core:view_profile")

    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)
        a_form = AddressUpdateForm(instance=address)  # 🔹 ADDED

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "a_form": a_form,  # 🔹 ADDED
    }
    return render(request, "edit_profile.html", context)

@login_required
def download_receipt_pdf(request, pk):
    receipt = get_object_or_404(
        DonationReceiptRequest,
        pk=pk,
        profile=request.user.profile,
        status="APPROVED"
    )

    assets = {
        "LOGO_URL": "https://res.cloudinary.com/dchlu4kif/image/upload/v1766995002/wallpaperflare.com_wallpaper_plphlg.jpg",
        "TEMPLE_BG_URL": "https://res.cloudinary.com/dchlu4kif/image/upload/v1766995002/temple_wwydkb.jpg",
        "DEITY_URL": "https://res.cloudinary.com/dchlu4kif/image/upload/v1766994993/sample_n9cu8f.jpg",
        "SIGNATURE_URL": "https://res.cloudinary.com/dchlu4kif/image/upload/v1767523466/signature_iiw9fy.png",
    }

    pdf = generate_receipt_pdf(receipt, assets)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Donation_Receipt_{receipt.id}.pdf"'
    )

    return response

def user_logout(request):
    logout(request)
    list(messages.get_messages(request))
    return redirect("core:home")

def home(request):
    return render(request, "index.html")

@cache_page(60 * 30)
def about(request):
    return render(request, "about.html")

@cache_page(60 * 30)
def trust_members(request):
    return render(request, "trust-members.html")

@cache_page(60 * 30)
def how_to_reach(request):
    return render(request, "how-to-reach.html")

@cache_page(60 * 30)
def donation_options(request):
    return render(request, "donation.html")

@cache_page(60 * 30)
def featured_news(request):
    return render(request, "featured-news.html")

@cache_page(60 * 30)
def contact(request):
    return render(request, "contact.html")

@cache_page(60 * 30)
def policy(request):
    return render(request, "policy.html")


#admin views
@staff_member_required
def staff_dashboard(request):
    """
    Central navigation page for staff actions
    """
    return render(
        request,
        "dashboard.html"
    )

@staff_member_required
def admin_receipt_list(request):
    receipts = DonationReceiptRequest.objects.all().order_by("-created_at")
    return render(request, "receipt_list.html", {"receipts": receipts})

@staff_member_required
def update_receipt_status(request, pk):
    receipt = get_object_or_404(DonationReceiptRequest, pk=pk)

    if request.method == "POST":
        status = request.POST.get("status")
        admin_remark = request.POST.get("admin_remark", "").strip()

        with transaction.atomic():

            receipt.status = status
            receipt.admin_remark = admin_remark
            receipt.save()

            # ─────────────── APPROVAL FLOW ───────────────
            if status == "APPROVED":

                # Prevent duplicate transaction creation
                txn, created = Transaction.objects.get_or_create(
                    transaction_id=receipt.receipt_id,
                    defaults={
                        "profile": receipt.profile,
                        "transaction_date": timezone.now(),
                        "donor_name": receipt.donor_name,
                        "amount": receipt.donation_amount,
                        "status": "APPROVED",
                    }
                )

                # Generate PDF
                pdf_bytes = generate_receipt_pdf(receipt)
                if not pdf_bytes:
                    raise Exception("PDF generation failed")

                # Attach PDF to transaction
                txn.receipt_file.save(
                    f"{receipt.receipt_id}.pdf",
                    ContentFile(pdf_bytes),
                    save=False
                )

                txn.status = "RECEIPT_SENT"
                txn.save()

                # Send approval email
                email = EmailMessage(
                    subject="Donation Receipt Approved",
                    body=(
                        f"Dear {receipt.donor_name},\n\n"
                        "Your donation has been verified and approved.\n"
                        "Please find your receipt attached.\n\n"
                        "Thank you for supporting our trust."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[receipt.email],
                )

                email.attach(
                    f"{receipt.receipt_id}.pdf",
                    pdf_bytes,
                    "application/pdf"
                )

                email.send(fail_silently=False)

            # ─────────────── REJECTION FLOW ───────────────
            else:
                EmailMessage(
                    subject="Donation Receipt Request Rejected",
                    body=(
                        f"Dear {receipt.donor_name},\n\n"
                        "Your receipt request has been rejected for the following reason:\n\n"
                        f"{admin_remark}\n\n"
                        "If you believe this is an error, please contact us."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[receipt.email],
                ).send(fail_silently=False)

        messages.success(request, "Receipt processed successfully.")
        return redirect("core:admin-receipt-list")

    return render(request, "receipt_detail.html", {"receipt": receipt})


@staff_member_required
def admin_transaction_list(request):
    successful_transactions = Transaction.objects.filter(
        status__in=["APPROVED", "RECEIPT_SENT"]
    ).order_by("-transaction_date")

    context = {
        "transactions": successful_transactions,
    }

    return render(
        request,
        "transaction_list.html",
        context
    )

