from django.contrib import admin
from .models import CustomUser, Client, Fournisseur, Produit, Stock
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Client)
admin.site.register(Fournisseur)
admin.site.register(Produit)
admin.site.register(Stock)

from django.contrib import admin
from .models import Client, Fournisseur, Produit, Stock, Commande  # ← ajoute Commande

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('client', 'produit', 'quantite', 'statut', 'date_commande')
    list_filter = ('statut', 'date_commande')
    search_fields = ('client__username', 'produit__designation')
