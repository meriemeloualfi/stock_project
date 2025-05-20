import os
from django.conf import settings
from weasyprint import HTML
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Client, Fournisseur, Produit, Stock, MouvementStock
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
import pathlib


# LOGIN
def custom_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'gestion/login.html', {'error': 'Identifiants incorrects'})
    return render(request, 'gestion/login.html')


# LOGOUT
def custom_logout(request):
    logout(request)
    return redirect('login')


# DASHBOARD
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

# PRODUITS
@login_required
def produits(request):
    query = request.GET.get("q", "")
    per_page = int(request.GET.get("per_page", 10))

    qs = Produit.objects.all()

    if query:
        qs = qs.filter(designation__icontains=query)

    paginator = Paginator(qs, per_page)
    page = request.GET.get("page")

    try:
        produits_page = paginator.get_page(page)
    except PageNotAnInteger:
        produits_page = paginator.get_page(1)
    except EmptyPage:
        produits_page = paginator.get_page(1)  # ou paginator.get_page(paginator.num_pages)

    context = {
        "produits": produits_page,
        "query": query,
        "per_page": per_page,
        "per_page_options": [10, 25, 50, 100],
    }
    return render(request, "gestion/produits/liste.html", context)


@login_required
def ajouter_produit(request):
    fournisseurs = Fournisseur.objects.all()

    if request.method == "POST":
        reference = request.POST.get("reference")
        designation = request.POST.get("designation")
        prix = request.POST.get("prix")
        quantite = request.POST.get("quantite")
        fournisseur_id = request.POST.get("fournisseur")
        image = request.FILES.get("image")

        # Validation quantité
        try:
            quantite_int = int(quantite)
            if quantite_int < 1:
                messages.error(request, "La quantité doit être au moins 1.", extra_tags="produit")
                return render(request, "gestion/produits/ajouter.html", {"fournisseurs": fournisseurs})
        except ValueError:
            messages.error(request, "Quantité invalide.", extra_tags="produit")
            return render(request, "gestion/produits/ajouter.html", {"fournisseurs": fournisseurs})

        # Validation fournisseur
        try:
            fournisseur = Fournisseur.objects.get(id=fournisseur_id)
        except Fournisseur.DoesNotExist:
            messages.error(request, "Fournisseur invalide.", extra_tags="produit")
            return render(request, "gestion/produits/ajouter.html", {"fournisseurs": fournisseurs})

        # Création produit
        produit = Produit(
            reference=reference,
            designation=designation,
            prix=prix,
            quantite=quantite_int,
            fournisseur=fournisseur,
            image=image
        )
        produit.save()

        # Message avec tag personnalisé
        messages.success(request, "Produit ajouté avec succès.", extra_tags="produit")
        return redirect("produits")

    return render(request, "gestion/produits/ajouter.html", {"fournisseurs": fournisseurs})

@login_required
def modifier_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    fournisseurs = Fournisseur.objects.all()

    if request.method == 'POST':
        produit.reference = request.POST.get('reference')
        produit.designation = request.POST.get('designation')
        produit.prix = float(request.POST.get('prix'))
        produit.quantite = int(request.POST.get('quantite'))
        produit.fournisseur_id = request.POST.get('fournisseur')

        # Gestion de l'image si un nouveau fichier est envoyé
        if 'image' in request.FILES:
            produit.image = request.FILES['image']

        produit.save()

        messages.success(request, "Produit modifié avec succès.")

        # Redirection vers la même page pour voir le toast
        return redirect('modifier_produit', id=produit.id)

    return render(request, 'gestion/produits/modifier.html', {
        'produit': produit,
        'fournisseurs': fournisseurs
    })

@login_required
def supprimer_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    produit.delete()
    return redirect('produits')



#client
@login_required
def clients(request):
    query = request.GET.get('q', '')
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10

    per_page_options = [5, 10, 20, 50]

    clients_qs = Client.objects.all()
    if query:
        clients_qs = clients_qs.filter(nom__icontains=query)  # ou autre filtre

    paginator = Paginator(clients_qs, per_page)
    page_number = request.GET.get('page')
    clients_page = paginator.get_page(page_number)

    context = {
        'clients': clients_page,
        'query': query,
        'per_page': per_page,
        'per_page_options': per_page_options,
    }
    return render(request, 'gestion/clients/liste.html', context)




@login_required
def ajouter_client(request):
    if request.method == "POST":
        Client.objects.create(
            nom     = request.POST["nom"],
            prenom  = request.POST["prenom"],
            email   = request.POST["email"],
            tel     = request.POST.get("tel",""),
            adresse = request.POST.get("adresse",""),
        )
        messages.success(request, "Client ajouté.")
        return redirect("clients")
    return render(request, "gestion/clients/ajouter.html", {"client": None})

@login_required
def modifier_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == "POST":
        client.nom     = request.POST["nom"]
        client.prenom  = request.POST["prenom"]
        client.email   = request.POST["email"]
        client.tel     = request.POST.get("tel","")
        client.adresse = request.POST.get("adresse","")
        client.save()
        messages.success(request, "Client modifié.")
        return redirect("clients")
    return render(request, "gestion/clients/modifier.html", {"client": client})

@login_required
def supprimer_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    messages.success(request, "Client supprimé.")
    return redirect("clients")



@login_required
def fournisseurs(request):
    query = request.GET.get("q", "")
    per_page = request.GET.get("per_page", 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10
    per_page_options = [5, 10, 20, 50]

    qs = Fournisseur.objects.all().order_by("libelle")
    if query:
        qs = qs.filter(libelle__icontains=query)

    paginator = Paginator(qs, per_page)
    page = request.GET.get("page")
    try:
        fournisseurs_page = paginator.get_page(page)
    except (PageNotAnInteger, EmptyPage):
        fournisseurs_page = paginator.get_page(1)

    return render(request, "gestion/fournisseur/liste.html", {
        "fournisseurs":    fournisseurs_page,
        "query":           query,
        "per_page":        per_page,
        "per_page_options": per_page_options,
    })

@login_required
def ajouter_fournisseur(request):
    if request.method == "POST":
        Fournisseur.objects.create(
            libelle = request.POST.get("libelle", ""),
            email   = request.POST.get("email", ""),
            tel     = request.POST.get("tel", ""),
            adresse = request.POST.get("adresse", ""),
        )
        messages.success(request, "Fournisseur ajouté.")
        return redirect("fournisseurs")
    return render(request, "gestion/fournisseur/ajouter.html", {"fournisseur": None})

@login_required
def modifier_fournisseur(request, fournisseur_id):
    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
    if request.method == "POST":
        fournisseur.libelle = request.POST.get("libelle", "")
        fournisseur.email   = request.POST.get("email", "")
        fournisseur.tel     = request.POST.get("tel", "")
        fournisseur.adresse = request.POST.get("adresse", "")
        fournisseur.save()
        messages.success(request, "Fournisseur modifié.")
        return redirect("fournisseurs")
    return render(request, "gestion/fournisseur/modifier.html", {"fournisseur": fournisseur})

@login_required
def supprimer_fournisseur(request, fournisseur_id):
    # si tu veux forcer POST :
    if request.method == "POST":
        fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
        fournisseur.delete()
        messages.success(request, "Fournisseur supprimé.")
    return redirect("fournisseurs")

def rapport_produit(request, id):
    produit = get_object_or_404(Produit, id=id)

    if produit.image:
        # Construction du chemin absolu avec pathlib
        image_path = pathlib.Path(settings.MEDIA_ROOT) / produit.image.name
        # Formatage du chemin en URL file:// pour Windows (3 slashs + slash avant chaque dossier)
        image_url = f'file:///{image_path.as_posix()}'
    else:
        image_url = None

    html_string = render_to_string('gestion/produits/rapport.html', {
        'produit': produit,
        'image_url': image_url
    })

    # IMPORTANT : indiquer base_url pour aider WeasyPrint à résoudre les chemins locaux
    html = HTML(string=html_string, base_url=settings.MEDIA_ROOT)
    result = html.write_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=rapport_produit_{produit.id}.pdf'
    response.write(result)
    print("IMAGE PATH = ", image_url)
    return response

@login_required
def stock_list(request):
    stocks = Stock.objects.all().order_by('-date_creation')
    return render(request, 'gestion/stock/liste_stocks.html', {'stocks': stocks})

@login_required
def ajouter_stock(request):
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        emplacement = request.POST.get('emplacement', '').strip()
        Stock.objects.create(nom=nom, emplacement=emplacement)
        messages.success(request, "Stock créé avec succès.")
        return redirect('stock')
    return render(request, 'gestion/stock/ajouter_stock.html')

@login_required
def detail_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    # on récupère l'historique des mouvements
    mouvements = MouvementStock.objects.filter(stock=stock).select_related('produit').order_by('-date')
    # on récupère **tous** les produits pour le <select>
    produits = Produit.objects.all().order_by('designation')

    return render(request, 'gestion/stock/detail.html', {
        'stock':     stock,
        'mouvements': mouvements,
        'produits':  produits,    # ← maintenant définie !
    })
@login_required
def ajouter_mouvement(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        produit = get_object_or_404(Produit, id=request.POST['produit'])
        q_entree = int(request.POST.get('entree', 0))
        q_sortie = int(request.POST.get('sortie', 0))

        # Création du mouvement
        MouvementStock.objects.create(
            stock=stock,
            produit=produit,
            quantite_entree=q_entree,
            quantite_sortie=q_sortie
        )

        # Mise à jour de la quantité réelle
        produit.quantite = produit.quantite + q_entree - q_sortie
        produit.save()

        # Message d’alerte si besoin
        if produit.en_alerte:
            messages.warning(
                request,
                f"⚠️ Stock bas pour « {produit.designation} » "
                f"(reste : {produit.quantite}, seuil : {produit.seuil})"
            )

        messages.success(request, "Mouvement ajouté.")
        return redirect('detail_stock', stock_id=stock.id)

    produits = Produit.objects.all().order_by('designation')
    return render(request, 'gestion/stock/ajouter_mouvement.html', {
        'stock': stock,
        'produits': produits
    })

@login_required
def pdf_rapport_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    mouvements = MouvementStock.objects.filter(stock=stock).select_related('produit')
    html_string = render_to_string('gestion/stock/rapport_stock.html', {
        'stock': stock,
        'mouvements': mouvements,
    })
    html = HTML(string=html_string, base_url=settings.MEDIA_ROOT)
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=rapport_stock_{stock_id}.pdf'
    return response