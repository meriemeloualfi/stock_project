from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
    reference   = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    prix        = models.DecimalField(max_digits=10, decimal_places=2)
    quantite    = models.IntegerField()
    seuil       = models.IntegerField(
        default=0,
        help_text="→ Alerte si quantité ≤ seuil"
    )
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    image = models.ImageField(upload_to='produits/', null=True, blank=True)

    def __str__(self):
        return self.designation

    @property
    def en_alerte(self):
        return self.quantite <= self.seuil


# models.py
class Stock(models.Model):
    nom = models.CharField(max_length=100, default="Stock Principal")
    emplacement = models.CharField(max_length=200, blank=True, default="Emplacement inconnu")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class MouvementStock(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    produit = models.ForeignKey('gestion.Produit', on_delete=models.CASCADE)  # ou appel correct de ton modèle Produit
    quantite_entree = models.IntegerField(default=0)
    quantite_sortie = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.produit} @ {self.stock} le {self.date}"

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
