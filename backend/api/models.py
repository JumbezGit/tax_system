from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Administrator')  # optional: force admin role for superusers

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=[('Taxpayer', 'Taxpayer'), ('Administrator', 'Administrator')],
        default='Taxpayer'
    )
    last_login_time = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # no additional required fields

    objects = UserManager()   # ← This is the critical line!

    def save(self, *args, **kwargs):
        if self.pk:
            self.last_login_time = timezone.now()
        super().save(*args, **kwargs)

class TaxpayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    date_of_birth = models.DateField()
    mobile_phone = models.CharField(max_length=20)
    national_id = models.CharField(max_length=50, unique=True)
    tin_number = models.CharField(max_length=50, unique=True)
    passport_number = models.CharField(max_length=50, blank=True)
    ward = models.CharField(max_length=100)
    street_village = models.CharField(max_length=100)
    house_number = models.CharField(max_length=50)
    taxpayer_type = models.CharField(max_length=20, choices=[('Individual', 'Individual'), ('Business', 'Business'), ('Organization', 'Organization')])
    property_type = models.CharField(max_length=20, choices=[('Residential', 'Residential'), ('Commercial', 'Commercial'), ('Industrial', 'Industrial')])
    property_location = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200, blank=True)
    registration_date = models.DateTimeField(default=timezone.now)
    account_status = models.CharField(max_length=20, default='Active')

class TaxType(models.Model):
    name = models.CharField(max_length=100)

class TaxAccount(models.Model):
    profile = models.OneToOneField(TaxpayerProfile, on_delete=models.CASCADE)
    total_tax_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    next_payment_due = models.DateField(null=True)
    tax_account_status = models.CharField(max_length=20, default='Active')

class PaymentRequest(models.Model):
    profile = models.ForeignKey(TaxpayerProfile, on_delete=models.CASCADE)
    tax_type = models.ForeignKey(TaxType, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[('Mobile Money', 'Mobile Money'), ('Pesapal', 'Pesapal'), ('Generate Control Number', 'Generate Control Number')])
    status = models.CharField(max_length=20, default='Pending')
    control_number = models.CharField(max_length=50, blank=True)
    provider_reference = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(default=timezone.now)