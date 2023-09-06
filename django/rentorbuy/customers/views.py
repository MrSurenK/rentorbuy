from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomerAccount, Rental
from .serializers import CustomerAccountSerializer, RentalSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class JwtDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        response = JWTAuthentication().authenticate(request)
        if response is not None:
            account, token = response

            print(account)
            print(account.id)
            print(account.email)

            return Response(token.payload)

        else:
            return Response('token error')

class CreateCustomerAccount(APIView):

    def post(self, request):
        nric = request.data.get('nric', None)
        email = request.data.get('email', None)

        if not nric or not email:
            return Response({'error': 'Both nric and email fields must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            customer_by_nric = CustomerAccount.objects.get(nric=nric)
        except CustomerAccount.DoesNotExist:
            customer_by_nric = None

        try:
            customer_by_email = CustomerAccount.objects.get(email=email)
        except CustomerAccount.DoesNotExist:
            customer_by_email = None

        if customer_by_nric or customer_by_email:
            if customer_by_nric and not customer_by_nric.is_active:
                customer_by_nric.is_active = True
                customer_by_nric.save()
                return Response({'message': 'Account with this nric reactivated'}, status=status.HTTP_200_OK)
            elif customer_by_email and not customer_by_email.is_active:
                customer_by_email.is_active = True
                customer_by_email.save()
                return Response({'message': 'Account with this email reactivated'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Account with this nric or email already exists.'},
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomerAccountSerializer(data=request.data)

        if serializer.is_valid():
            user = CustomerAccount.objects.create_user(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCustomerAccount(APIView):
    permission_classes = (IsAuthenticated,)
    def delete(self, request):
        nric = request.user.nric
        try:
            customer = CustomerAccount.objects.get(nric=nric) #nric is the param
        except CustomerAccount.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Check if only 'is_active' field is present in the request data
        if set(request.data.keys()) == {'is_active'}:
            serializer = CustomerAccountSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Only the is_active field can be updated.'}, status=status.HTTP_400_BAD_REQUEST)

class GetCustomerAccount(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        nric = request.user.nric
        if nric is None:
            return Response({"error": "NRIC is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = CustomerAccount.objects.get(nric=nric)
        except CustomerAccount.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerAccountSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomerRentalHistory(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        nric = request.user.nric
        if nric is None:
            return Response({"error": "NRIC is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            customer = CustomerAccount.objects.get(nric=nric)
        except CustomerAccount.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        rentals = Rental.objects.filter(customer_nric=customer)
        serializer = RentalSerializer(rentals, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# class CustomerSaleHistory(APIView):
#     def post(self, request):











