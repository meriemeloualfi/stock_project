from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
        ('fournisseur', 'Fournisseur'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')


class Client(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="client_profile", null=True)
    nom = models.CharField(max_length=100, default='Nom inconnu')
    prenom = models.CharField(max_length=100, default='Prénom inconnu')
    email = models.EmailField(default='exemple@email.com')
    tel = models.CharField(max_length=20, default='0000000000')
    adresse = models.TextField(default='Adresse inconnue')

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Fournisseur(models.Model):
    libelle = models.CharField(max_length=100, default="Fournisseur inconnu")
    email = models.EmailField(default="inconnu@example.com")
    tel = models.CharField(max_length=20, default="0000000000")
    adresse = models.CharField(max_length=255, default="Adresse inconnue")

    def __str__(self):
        return self.libelle


class Produit(models.Model):
    reference = models.CharField(max_length=100, default='REF-000')
    designation = models.CharField(max_length=100, default='Sans désignation')
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.IntegerField()
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.reference} - {self.designation}"


class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite_entree = models.IntegerField(default=0)
    quantite_sortie = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stock de {self.produit.reference} - {self.date.strftime('%Y-%m-%d %H:%M')}"

from django.db import models
from django.conf import settings

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de confirmation'),
        ('en_cours', 'En cours de livraison'),
        ('livree', 'Livrée'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')  # ← AJOUTÉ

    def __str__(self):
        return f"Commande {self.id} - {self.produit.designation}"

