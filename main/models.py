from django.db import models,transaction
from django.utils import timezone
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage  # ADD THIS LINE
# Create your models here.

from django.db import models

class EmailLoginToken(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=10)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Profile(models.Model):
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    )

    ID_TYPE_CHOICES = (
        ("PAN", "PAN Card"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    donor_name = models.CharField(max_length=150,null=True,blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,default="M")
    photo_id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES,blank=True, null=True)
    photo_id_number = models.CharField(max_length=50,blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    avatar = models.ImageField(
        upload_to="profile_images/", 
        blank=True, null=True,
        storage=MediaCloudinaryStorage()  # ADD THIS LINE
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="address")
    address_line = models.TextField()
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    village_or_post = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.profile.donor_name} - {self.pincode}"


class Transaction(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("RECEIPT_SENT", "Receipt Sent"),
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="transactions")

    transaction_id = models.CharField(max_length=100, unique=True)
    transaction_date = models.DateTimeField()
    donor_name = models.CharField(max_length=150)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    receipt_file = models.FileField(
        upload_to="receipts/",
        blank=True,
        null=True,
        storage=MediaCloudinaryStorage()
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.donor_name}"


# models.py


class DonationReceiptRequest(models.Model):
    DONOR_TYPE_CHOICES = (
        ("INDIAN", "Indian"),
        ("NON_INDIAN", "Non-Indian"),
    )
    
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )
    
    receipt_id = models.CharField(
    max_length=20,
    unique=True,
    null=True,
    blank=True,
    editable=False,
    db_index=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    admin_remark = models.TextField(blank=True, null=True)

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="receipt_requests")

    donor_type = models.CharField(max_length=20, choices=DONOR_TYPE_CHOICES)

    donor_name = models.CharField(max_length=200)
    pan_number = models.CharField(max_length=10, blank=True, null=True)

    donation_amount = models.DecimalField(max_digits=10, decimal_places=2)

    address = models.TextField()
    country = models.CharField(max_length=100,default="India")
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    email = models.EmailField()
    mobile = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.donor_name} - {self.donation_amount}"
    
    def save(self, *args, **kwargs):
        # IMPORTANT: check for both None and empty string (legacy safety)
        if not self.receipt_id:
            with transaction.atomic():
                year = timezone.now().year

                last = (
                    DonationReceiptRequest.objects
                    .select_for_update()
                    .filter(receipt_id__startswith=f"REC-{year}")
                    .order_by("-receipt_id")
                    .first()
                )

                if last:
                    last_number = int(last.receipt_id.split("-")[-1])
                    next_number = last_number + 1
                else:
                    next_number = 1

                self.receipt_id = f"REC-{year}-{next_number:06d}"

        super().save(*args, **kwargs)


# class Photo(models.Model):
#     title = models.CharField(max_length=50)
#     image = models.ImageField(upload_to="photos/")
    
#     def __str__(self):
#         return self.title