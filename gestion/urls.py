from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  

    path('', views.dashboard, name='dashboard'),
    path('login/', views.custom_login, name='login'),

    path('clients/', views.clients, name='clients'),
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
    path('clients/<int:client_id>/modifier/', views.modifier_client, name='modifier_client'),
    path('clients/<int:client_id>/supprimer/', views.supprimer_client, name='supprimer_client'),

     
    path('fournisseurs/', views.fournisseurs, name='fournisseurs'),
    path('fournisseurs/ajouter/', views.ajouter_fournisseur, name='ajouter_fournisseur'),
    path(
        'fournisseurs/modifier/<int:fournisseur_id>/',
        views.modifier_fournisseur,
        name='modifier_fournisseur'
    ),
     path(
        'fournisseurs/supprimer/<int:fournisseur_id>/',
        views.supprimer_fournisseur,
        name='supprimer_fournisseur'
    ),


    path('produits/', views.produits, name='produits'),
    path('produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produits/modifier/<int:id>/', views.modifier_produit, name='modifier_produit'),
    path('produits/supprimer/<int:id>/', views.supprimer_produit, name='supprimer_produit'),
    path('produits/<int:id>/rapport/', views.rapport_produit, name='rapport_produit'),


    path('stock/', views.stock_list, name='stock'),
    path('stock/ajouter/', views.ajouter_stock, name='ajouter_stock'),
    path('stock/<int:stock_id>/', views.detail_stock, name='detail_stock'),
    path('stock/<int:stock_id>/rapport/', views.pdf_rapport_stock, name='pdf_rapport_stock'),
    path('stock/<int:stock_id>/mouvement/', views.ajouter_mouvement, name='ajouter_mouvement'),

    
    path('logout/', views.custom_logout, name='logout'),

    path('register/', views.register_client, name='register'),
path('client/dashboard/', views.dashboard_client, name='dashboard_client'),
path('client/profil/', views.modifier_profil_client, name='modifier_profil'),
path('client/produits/', views.produits_client, name='produits_client'),
path('client/produits/commande/<int:produit_id>/', views.commander_produit, name='commander_produit'),
path('client/commandes/', views.mes_commandes, name='mes_commandes'),

]
