from django.urls import path, include
from . import views
from graphene_django.views import GraphQLView
from django.views.generic import TemplateView



app_name = 'recipelist'
urlpatterns=[
    path("", views.index, name='index'),
    path("index.html/", views.index, name='index'),

    path("get_ingredients/", views.get_ingredients, name='get_ingredients'),
    path('search/', views.search, name='search'),

    path('adjusted_search/', views.adjusted_search, name='adjusted_search'),
    path('grocery_list/', views.grocery_list, name='grocery_list'),
    #path("graphql", GraphQLView.as_view(graphiql=True), schema=schema),
    path("graphql/", (GraphQLView.as_view(graphiql=True))),
    #path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    #path('login_heb/', views.login_heb, name='login_heb'),
    path('api_test/', views.api_test, name='api_test'),
    #path('commerce__test/', views.commerce_test, name='commerce_test'),
    path('send_text/', views.send_text, name='send_text'),

    path('success_page/', views.success_page, name='success_page'),  # Define a success page view

]
