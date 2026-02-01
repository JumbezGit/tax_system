from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import RegisterSerializer, ProfileSerializer, LoginSerializer, TaxAccountSerializer, PaymentRequestSerializer, UserSerializer
from .models import User, TaxpayerProfile, TaxAccount, PaymentRequest, TaxType
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdmin
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
import uuid

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create profile (add logic to handle profile data from request)
            profile_data = request.data  # Assume all profile fields in request
            profile_serializer = ProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save(user=user)
                # Create TaxAccount
                TaxAccount.objects.create(profile=profile)
            else:
                user.delete()
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "User registered"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': user.role
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return TaxpayerProfile.objects.get(user=self.request.user)

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = TaxpayerProfile.objects.get(user=request.user)
        account = TaxAccount.objects.get(profile=profile)
        data = TaxAccountSerializer(account).data
        # Add more summary logic if needed
        return Response(data)

class PaymentRequestView(generics.CreateAPIView):
    serializer_class = PaymentRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        profile = TaxpayerProfile.objects.get(user=self.request.user)
        if serializer.validated_data['payment_method'] == 'Generate Control Number':
            serializer.validated_data['control_number'] = str(uuid.uuid4())[:8].upper()
        serializer.save(profile=profile)
        # Simulate update to account (in real, async or webhook)

class MarkPaymentPaidView(APIView):
    permission_classes = [IsAuthenticated]  # Or IsAdmin for production

    def post(self, request, pk):
        payment = PaymentRequest.objects.get(pk=pk)
        payment.status = 'Paid'
        payment.save()
        account = payment.profile.taxaccount
        account.paid_amount += payment.amount
        account.outstanding_balance -= payment.amount
        account.save()
        return Response({"message": "Payment marked paid"})

# Admin views
class AdminMetricsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        metrics = {
            'total_taxpayers': TaxpayerProfile.objects.count(),
            'total_revenue': PaymentRequest.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0,
            # Add more
        }
        return Response(metrics)

class AdminUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()

# Add UnpaidUsersPrintView (returns JSON, frontend handles print)
class UnpaidUsersPrintView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        unpaid = TaxAccount.objects.filter(outstanding_balance__gt=0)
        data = [{"name": acc.profile.user.get_full_name(), "balance": acc.outstanding_balance} for acc in unpaid]
        return Response(data)