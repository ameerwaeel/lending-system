from celery import shared_task
from loan_app.models import Payment, Borrower
from django.core.exceptions import ObjectDoesNotExist
import logging

@shared_task
def process_payments_every_hour():
    pending_payments = Payment.objects.filter(is_paid=False)

    for payment in pending_payments:
        try:
            borrower = Borrower.objects.get(user=payment.loan.borrower.user)
        except ObjectDoesNotExist:
            continue  # إذا لم يكن المقترض موجودًا، تجاهل هذه المدفوعات

        if borrower.balance >= payment.amount:
            borrower.balance -= payment.amount
            borrower.save()
            payment.is_paid = True
            payment.save()

            if all(p.is_paid for p in payment.loan.payments.all()):
                payment.loan.status = 'completed'
                payment.loan.save()




@shared_task
def process_payment_task(payment_id, user_id):
    try:
        payment = Payment.objects.select_related('loan').get(id=payment_id)
        borrower = Borrower.objects.get(user_id=user_id)

        if borrower.balance < payment.amount:
            return {"error": "Insufficient balance."}

        borrower.balance -= payment.amount
        borrower.save()

        payment.is_paid = True
        payment.save()

        if all(p.is_paid for p in payment.loan.payments.all()):
            payment.loan.status = 'completed'
            payment.loan.save()

        return {"success": "Payment processed successfully."}

    except Payment.DoesNotExist:
        logging.error(f"Payment with id {payment_id} does not exist.")
        return {"error": "Payment not found."}
    except Borrower.DoesNotExist:
        logging.error(f"Borrower with user_id {user_id} does not exist.")
        return {"error": "Borrower not found."}
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"error": "An unexpected error occurred."}
