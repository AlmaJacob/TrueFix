from django.urls import path
from . import views


urlpatterns = [
    path('',views.company_login),
    path('logout',views.company_logout),
    path('register',views.register),

    # ------------COMPANY---------------
    
    path('company',views.company_home),
    path('logout',views.company_logout),
    # path('add_pro',views.add_pro),
    # path('delete_product/<pid>',views.delete_product),
    # path('edit/<pid>',views.edit_product),
    # path('view_booking',views.view_bookings),
    # path('cancel_order/<pid>',views.cancel_order),
]