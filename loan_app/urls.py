from django.urls import path 
# from . import views
app_name="loan_app"
from . import views

from .views import LoanRequestView, LoanListView, MakePaymentView, LoanDetailView

urlpatterns = [
    path('LoanRequestView/', LoanRequestView.as_view(), name='LoanRequestView'),
    path('LoanListView/', LoanListView.as_view(), name='LoanListView'),
    path('OfferLoanView/<int:loan_id>/', views.OfferLoanView.as_view(), name='OfferLoanView'),
    path('MakePaymentView/<int:payment_id>/', MakePaymentView.as_view(), name='MakePaymentView'),
    path('LoanListView/<int:loan_id>/', LoanDetailView.as_view(), name='LoanDetailView'),

]


