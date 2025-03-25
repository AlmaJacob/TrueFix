from django.urls import path
from . import views
# from .views import buy_now



from django.urls import path
from . import views

urlpatterns = [
    path('cancel_booking/<int:bid>/', views.cancel_booking, name='cancel_booking'),  # ✅ Cancel a booking
    path('bookings/', views.user_bookings, name='bookings_page'),  # ✅ Ensure this view exists
]







urlpatterns = [
    path('login', views.service_login),
    path('logout', views.service_logout),
    path('register', views.register),

    # ------------COMPANY-------------
    path('company', views.company_home),
    path('add_service', views.add_service),
    path('delete_service/<int:sid>', views.delete_service),
    path('edit_service/<int:sid>', views.edit_service),
    # path('view_bookings', views.view_bookings),
    # path('cancel_booking/<int:bid>', views.cancel_booking),
    # path('confirm_order/<order_id>',views.confirm_order, name='confirm_order'),
    # path('cancel_order/<order_id>',views.cancel_order, name='cancel_order'),

    path('confirm_order/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    # ------------USER-------------
    path('', views.user_home),
    path('about', views.about),
    path('blog', views.blog),
    path('contact', views.contact),
    path('book_service/<int:sid>', views.book_service),
    path('view_service/<pid>',views.view_service),
    # path('_ser', views.bookings),
    # path('cart_service_book/<int:sid>', views.cart_servi),
    # path('service_book/<int:sid>', views.service_book),
    path('cancel_booking/1/<int:bid>/', views.cancel_booking, name='cancel_booking'),
    # path('order_booking/<int:sid>')
    path('book_service/<int:id>/',views.buy_now, name='buy_now'),
    # path('payment/<pid>', payment_page, name='payment_page'),
    path('order_payment', views.order_payment, name='order_payment'),
    # path('order_success',views.order_success),
    path('search/', views.search_service, name='search_service'),
    path('profile',views.user_profile),
    path('update_profile',views.update_profile,name='update_profile'),
    path('delete_account', views.delete_account, name='delete_account'),
    path('callback/', views.callback, name='callback'),
    path('add-address/', views.add_address, name='add_address'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('view_bookings', views.view_bookings),
    path('update_booking', views.update_booking_status),
    path('bookings', views.user_bookings),
    # path('toggle_confirmation/<int:order_id>/<str:order_type>/', views.toggle_confirmation, name='toggle_confirmation'),

]