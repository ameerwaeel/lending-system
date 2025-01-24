from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Borrower, Lender, Loan, Payment
from .serializers import LoanSerializer, PaymentSerializer
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from loan_app.tasks import process_payment_task
from celery.result import AsyncResult
from django.core.cache import cache
import logging

class LoanRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            borrower = Borrower.objects.get(user=request.user)
        except Borrower.DoesNotExist:
            return Response({"error": "Borrower not found."}, status=status.HTTP_404_NOT_FOUND)

        amount = request.data.get('amount')
        term_in_months = request.data.get('term_in_months')

        if not amount or not term_in_months:
            return Response({"error": "Amount and term_in_months are required."}, status=status.HTTP_400_BAD_REQUEST)

        loan = Loan.objects.create(
            borrower=borrower,
            amount=amount,
            term_in_months=term_in_months
        )
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


class LoanListView(APIView):
    def get(self, request):
        cache_key = 'loan_list_pending' 
        loans = cache.get(cache_key)

        if not loans:
            loans = Loan.objects.filter(status='pending', lender__isnull=True)
            cache.set(cache_key, loans, timeout=3600)

        return Response(LoanSerializer(loans, many=True).data)
    
from django.db import transaction

class OfferLoanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, loan_id):
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            lender = Lender.objects.get(user=request.user)
        except Lender.DoesNotExist:
            return Response({"error": "Lender not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            loan = Loan.objects.get(id=loan_id, status='pending')
        except Loan.DoesNotExist:
            return JsonResponse({'error': 'Loan not found or not pending'}, status=404)

        # Verify lender balance
        total_due = loan.total_amount_due() + Decimal('3.75')
        if lender.balance < total_due:
            return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                loan.lender = lender
                loan.status = 'funded'
                loan.funded_at = now()
                loan.save()

                lender.balance -= total_due
                lender.save()

                for month in range(loan.term_in_months):
                    Payment.objects.create(
                        loan=loan,
                        amount=loan.total_amount_due() / loan.term_in_months,
                        due_date=now() + timedelta(days=30 * (month + 1))
                    )
                
        except Exception as e:
            logging.error(f"Error while processing loan offer: {str(e)}")
            return Response({"error": "An error occurred while processing the loan."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(LoanSerializer(loan).data)





class MakePaymentView(APIView):
    def post(self, request, payment_id):
        user_id = request.user.id

        task = process_payment_task.delay(payment_id, user_id)

        try:
            result = AsyncResult(task.id)
            result_data = result.get(timeout=30)  
        except Exception as e:
            logging.error(f"Error processing payment task: {str(e)}")
            return Response({"error": "Task processing failed.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if "error" in result_data:
            return Response({"error": result_data["error"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result_data, status=status.HTTP_200_OK)


class LoanDetailView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
            return Response(LoanSerializer(loan).data)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)
        
  
        
   