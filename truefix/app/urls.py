from django.urls import path
from . import views
from .views import buy_now
urlpatterns = [
    path('', views.service_login),
    path('logout', views.service_logout),
    path('register', views.register),

    # ------------COMPANY-------------
    path('company', views.company_home),
    path('logout', views.service_logout),
    path('add_service', views.add_service),
    path('delete_service/<int:sid>', views.delete_service),
    path('edit_service/<int:sid>', views.edit_service),
    path('view_bookings', views.view_bookings),
    path('cancel_booking/<int:bid>', views.cancel_booking),
     path('cancel_booking/<int:bid>', views.cancel_booking),

    # ------------USER-------------
    path('user_home', views.user_home),
    path('about', views.about),
    path('blog', views.blog),
    path('contact', views.contact),
    path('user_booking/<int:sid>', views.user_bookings),
    path('book_service/<int:sid>', views.book_service),
    path('view_service/<pid>',views.view_service),
    # path('_ser', views.bookings),
    # path('cart_service_book/<int:sid>', views.cart_servi),
    # path('service_book/<int:sid>', views.service_book),
    path('cancel', views.cancel_booking),
    # path('order_booking/<int:sid>')
    path('book_service/<int:id>/',views.buy_now, name='buy_now'),
    # path('payment/<pid>', payment_page, name='payment_page'),
    path("order_payment", views.order_payment, name="order_payment")

]