from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Client, Fournisseur, Produit, Stock, Commande
from .forms import ClientRegisterForm


# AUTHENTIFICATION
def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'client':
                return redirect('dashboard_client')
            elif user.role == 'fournisseur':
                return redirect('fournisseur_home')
            else:
                return redirect('dashboard')
        else:
            return render(request, 'gestion/login.html', {'error': 'Identifiants incorrects'})
    return render(request, 'gestion/login.html')

def custom_logout(request):
    logout(request)
    return redirect('login')


# DASHBOARD ADMIN
@login_required
def dashboard(request):
    total_produits = Produit.objects.count()
    total_clients = Client.objects.count()
    total_fournisseurs = Fournisseur.objects.count()
    total_stock = Stock.objects.count()

    return render(request, 'gestion/dashboard.html', {
        'total_produits': total_produits,
        'total_clients': total_clients,
        'total_fournisseurs': total_fournisseurs,
        'total_stock': total_stock,
    })


# CLIENT
@login_required
def clients(request):
    clients = Client.objects.all()

    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        email = request.POST['email']
        tel = request.POST['tel']
        adresse = request.POST['adresse']

        if client_id:
            client = get_object_or_404(Client, id=client_id)
            client.nom = nom
            client.prenom = prenom
            client.email = email
            client.tel = tel
            client.adresse = adresse
            client.save()
        else:
            Client.objects.create(nom=nom, prenom=prenom, email=email, tel=tel, adresse=adresse)

        return redirect('clients')

    return render(request, 'gestion/clients.html', {'clients': clients})


@login_required
def supprimer_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    return redirect('clients')


def register_client(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'client'
            user.save()

            Client.objects.create(
                user=user,
                nom=form.cleaned_data['nom'],
                prenom=form.cleaned_data['prenom'],
                email=form.cleaned_data['email'],
                tel=form.cleaned_data['tel'],
                adresse=form.cleaned_data['adresse'],
            )
            return redirect('login')
    else:
        form = ClientRegisterForm()
    return render(request, 'gestion/register_client.html', {'form': form})


@login_required
def dashboard_client(request):
    if request.user.role != 'client':
        return redirect('dashboard')

    commandes_en_attente = Commande.objects.filter(client=request.user, statut='en_attente').count()
    commandes_en_cours = Commande.objects.filter(client=request.user, statut='en_cours').count()
    commandes_livrees = Commande.objects.filter(client=request.user, statut='livree').count()

    return render(request, 'gestion/dashboard_client.html', {
        'commandes_en_attente': commandes_en_attente,
        'commandes_en_cours': commandes_en_cours,
        'commandes_livrees': commandes_livrees,
    })


@login_required
def modifier_profil_client(request):
    client = Client.objects.get(user=request.user)
    if request.method == 'POST':
        client.nom = request.POST.get('nom')
        client.prenom = request.POST.get('prenom')
        client.email = request.POST.get('email')
        client.tel = request.POST.get('tel')
        client.adresse = request.POST.get('adresse')
        client.save()
        return redirect('dashboard_client')
    return render(request, 'gestion/modifier_profil.html', {'client': client})


# PRODUITS (ADMIN)
@login_required
def produits(request):
    produits = Produit.objects.all()
    fournisseurs = Fournisseur.objects.all()

    if request.method == 'POST':
        produit_id = request.POST.get('produit_id')
        reference = request.POST['reference']
        designation = request.POST['designation']
        prix = float(request.POST['prix'])
        quantite = int(request.POST['quantite'])
        fournisseur = get_object_or_404(Fournisseur, id=request.POST['fournisseur'])

        if produit_id:
            produit = get_object_or_404(Produit, id=produit_id)
            produit.reference = reference
            produit.designation = designation
            produit.prix = prix
            produit.quantite = quantite
            produit.fournisseur = fournisseur
            produit.save()
        else:
            Produit.objects.create(reference=reference, designation=designation, prix=prix, quantite=quantite, fournisseur=fournisseur)
        return redirect('produits')

    return render(request, 'gestion/produits.html', {'produits': produits, 'fournisseurs': fournisseurs})


@login_required
def supprimer_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    produit.delete()
    return redirect('produits')


# PRODUITS (CLIENT)
@login_required
def produits_client(request):
    produits = Produit.objects.all()
    return render(request, 'gestion/produits_client.html', {'produits': produits})


@login_required
def commander_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    quantite = int(request.POST.get('quantite', 1))
    if quantite > 0 and quantite <= produit.quantite:
        Commande.objects.create(client=request.user, produit=produit, quantite=quantite)
        produit.quantite -= quantite
        produit.save()
    return redirect('produits_client')


@login_required
def mes_commandes(request):
    commandes = Commande.objects.filter(client=request.user).order_by('-date_commande')
    return render(request, 'gestion/mes_commandes.html', {'commandes': commandes})


# FOURNISSEURS
@login_required
def fournisseurs(request):
    if request.method == 'POST':
        fournisseur_id = request.POST.get("fournisseur_id")
        libelle = request.POST.get("libelle")
        email = request.POST.get("email")
        tel = request.POST.get("tel")
        adresse = request.POST.get("adresse")

        if fournisseur_id:
            fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
            fournisseur.libelle = libelle
            fournisseur.email = email
            fournisseur.tel = tel
            fournisseur.adresse = adresse
            fournisseur.save()
        else:
            Fournisseur.objects.create(libelle=libelle, email=email, tel=tel, adresse=adresse)
        return redirect("fournisseurs")

    fournisseurs = Fournisseur.objects.all()
    return render(request, "gestion/fournisseurs.html", {"fournisseurs": fournisseurs})


@login_required
def supprimer_fournisseur(request, id):
    fournisseur = get_object_or_404(Fournisseur, id=id)
    fournisseur.delete()
    messages.success(request, "Fournisseur supprimé")
    return redirect('fournisseurs')


# STOCK
@login_required
def stock_view(request):
    produits = Produit.objects.all()
    stocks = Stock.objects.order_by('-date')

    if request.method == 'POST':
        produit = get_object_or_404(Produit, id=request.POST['produit'])
        entree = int(request.POST.get('quantite_entree', 0))
        sortie = int(request.POST.get('quantite_sortie', 0))

        if entree == 0 and sortie == 0:
            return render(request, 'gestion/stock.html', {
                'produits': produits, 'stocks': stocks,
                'error': "Veuillez entrer une quantité d'entrée ou de sortie."
            })

        Stock.objects.create(produit=produit, quantite_entree=entree, quantite_sortie=sortie, date=timezone.now())
        produit.quantite += entree - sortie
        produit.save()
        return redirect('stock')

    return render(request, 'gestion/stock.html', {'produits': produits, 'stocks': stocks})