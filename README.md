# 🚀 SiteForge — CMS No-Code avec Django

Plateforme complète de création de sites web no-code, avec éditeur drag & drop, domaines personnalisés et abonnements Stripe.

---

## 📋 Fonctionnalités

- **5 types de sites** : Portfolio, E-Commerce, E-Shop, E-Art/Galerie, Blog/News
- **15 templates** (3 designs par type de site)
- **Éditeur visuel** drag & drop avec panneau de propriétés en temps réel
- **Aperçu responsive** Desktop / Tablette / Mobile
- **Domaines personnalisés** avec instructions DNS CNAME automatiques
- **Abonnement mensuel/annuel** via Stripe avec **21 jours d'essai gratuit**
- **Dashboard multi-sites** : créez autant de sites que vous voulez
- **Personnalisation globale** : couleurs, typographies, navbar

---

## 🗂️ Structure du projet

```
siteforge/
├── siteforge/              # Configuration Django principale
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # Authentification & profils utilisateurs
│   ├── models.py           # User custom avec propriétés abonnement
│   ├── views.py            # register, login, logout, profile
│   ├── forms.py
│   └── urls.py
├── billing/                # Abonnements & facturation
│   ├── models.py           # Subscription, Invoice, Plan
│   ├── views.py            # Subscribe, cancel, webhook Stripe
│   └── urls.py
├── builder/                # Cœur du CMS
│   ├── models.py           # Site, Page, Section, Domain, Media
│   ├── views.py            # Éditeur + API REST (section/design/publish)
│   ├── middleware.py       # Routage domaines personnalisés
│   └── urls.py
├── dashboard/              # Interface utilisateur
│   ├── views.py            # Landing, dashboard home, site detail
│   └── urls.py
├── templates/
│   ├── base.html           # Template de base (dark theme)
│   ├── landing/index.html  # Page d'accueil marketing
│   ├── accounts/           # login.html, register.html, profile.html
│   ├── dashboard/          # home.html, site_detail.html, base.html
│   ├── builder/            # create_step1/2/3.html, editor.html
│   ├── billing/            # home.html, subscribe.html, cancel.html
│   └── sites/              # Templates de rendu public (15 fichiers)
├── static/
├── media/
├── requirements.txt
└── manage.py
```

---

## ⚡ Installation

### 1. Prérequis

```bash
Python 3.10+
pip
```

### 2. Cloner & installer les dépendances

```bash
cd siteforge
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Variables d'environnement

Créez un fichier `.env` à la racine :

```env
SECRET_KEY=votre-secret-key-django-tres-longue-et-aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données (SQLite par défaut, PostgreSQL recommandé en prod)
DATABASE_URL=sqlite:///db.sqlite3

# Stripe
STRIPE_PUBLIC_KEY=pk_test_xxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx
STRIPE_MONTHLY_PRICE_ID=price_xxxxxxxxxxxx
STRIPE_YEARLY_PRICE_ID=price_xxxxxxxxxxxx

# Email (Gmail ou SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre@email.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Votre domaine principal
MAIN_DOMAIN=siteforge.io
TRIAL_DAYS=21
```

### 4. Migrations & superuser

```bash
python manage.py makemigrations accounts billing builder dashboard
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### 5. Lancer le serveur

```bash
python manage.py runserver
```

Ouvrez : **http://localhost:8000**

---

## 💳 Configuration Stripe

### Créer les produits Stripe

1. Allez sur https://dashboard.stripe.com/products
2. Créez un produit **"SiteForge Abonnement"**
3. Ajoutez deux prix :
   - **Mensuel** : 9,99 € / mois → copiez le `price_id` dans `.env`
   - **Annuel** : 95,88 € / an (7,99€/mois) → copiez le `price_id`

### Webhook Stripe (production)

```bash
# CLI Stripe pour le dev local
stripe listen --forward-to localhost:8000/billing/webhook/

# En production, configurez le webhook sur :
# https://dashboard.stripe.com/webhooks
# URL : https://votre-domaine.com/billing/webhook/
# Événements : customer.subscription.updated, invoice.payment_succeeded, etc.
```

---

## 🌐 Configuration domaines personnalisés

### DNS côté client (ce que vos utilisateurs font)

```
Type  : CNAME
Nom   : @ ou www
Valeur: sites.siteforge.io
TTL   : 3600
```

### Nginx (production)

```nginx
server {
    listen 80;
    server_name *.siteforge.io;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Pour les domaines personnalisés
server {
    listen 80 default_server;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

### SSL avec Certbot (wildcard)

```bash
certbot certonly --dns-cloudflare \
  -d "*.siteforge.io" \
  -d "siteforge.io"
```

---

## 🏗️ Modèles de données

### Site
```python
Site(
  user, name, slug, site_type,   # portfolio/ecommerce/eshop/eart/blog
  template_id,                    # ex: portfolio_minimal
  status,                         # draft/published/suspended
  settings={                      # JSON de personnalisation
    "colors": {"primary","bg","text"},
    "fonts":  {"heading","body"},
    "navbar": {"sticky","transparent"}
  }
)
```

### Section
```python
Section(
  page, section_type,   # hero/about/product_grid/gallery/contact/...
  order,                # position drag & drop
  is_visible,
  content={...},        # données spécifiques (titre, texte, items...)
  settings={...}        # bg_color, padding, text_align
)
```

### Subscription
```python
Subscription(
  user, plan,           # monthly/yearly
  status,               # trialing/active/past_due/canceled
  trial_end,            # J+21 à l'inscription
  stripe_subscription_id,
  stripe_customer_id
)
```

---

## 🎨 Ajouter un nouveau template

1. Ajoutez l'entrée dans `builder/models.py` → `SITE_TEMPLATES`
2. Créez le template HTML dans `templates/sites/<template_id>.html`
3. C'est tout !

```python
# Dans SITE_TEMPLATES['portfolio'] :
{'id': 'portfolio_mydesign', 'name': 'My Design', 'preview': 'preview.jpg',
 'colors': ['#fff', '#000', '#ff0000'], 'style': 'bold'}
```

---

## 🧩 Ajouter un nouveau type de section

Dans `builder/models.py`, ajoutez dans `SECTION_TYPES` :
```python
('ma_section', 'Ma Section'),
```

Dans `builder/templates/builder/editor.html`, ajoutez les champs dans `fieldMap`.

Dans le template de site, gérez le rendu :
```html
{% elif section.section_type == 'ma_section' %}
  <div>{{ section.content.mon_champ }}</div>
```

---

## 🚀 Déploiement production (Gunicorn + PostgreSQL)

### settings_prod.py
```python
from .settings import *
DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'siteforge_db',
        'USER': 'siteforge_user',
        'PASSWORD': 'motdepasse',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
STATIC_ROOT = '/var/www/siteforge/static/'
MEDIA_ROOT = '/var/www/siteforge/media/'
```

### Gunicorn
```bash
gunicorn siteforge.wsgi:application \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Systemd service
```ini
[Unit]
Description=SiteForge Django
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/siteforge
ExecStart=/var/www/siteforge/venv/bin/gunicorn siteforge.wsgi:application --workers 4 --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📡 API REST interne (Builder)

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/builder/api/site/<id>/settings/` | Mettre à jour les paramètres design |
| POST | `/builder/api/site/<id>/publish/` | Publier le site |
| POST | `/builder/api/site/<id>/domain/` | Ajouter un domaine |
| POST | `/builder/api/site/<id>/media/` | Upload médias |
| GET  | `/builder/api/domain/<id>/verify/` | Vérifier DNS |
| POST | `/builder/api/page/<id>/sections/add/` | Ajouter une section |
| POST | `/builder/api/page/<id>/sections/reorder/` | Réordonner (drag & drop) |
| POST | `/builder/api/section/<id>/` | Modifier contenu/settings |
| DELETE | `/builder/api/section/<id>/delete/` | Supprimer une section |

---

## 📁 Types de sections disponibles

| Type | Description |
|------|-------------|
| `hero` | Banner principal avec titre, sous-titre et CTA |
| `about` | À propos avec texte et image |
| `services` / `features` | Grille de services/fonctionnalités |
| `portfolio_grid` | Grille de projets portfolio |
| `product_grid` | Grille de produits e-commerce |
| `gallery` | Galerie d'images |
| `blog_grid` | Grille d'articles |
| `testimonials` | Témoignages clients |
| `contact` | Formulaire de contact |
| `newsletter` | Inscription newsletter |
| `pricing` | Tableau de tarifs |
| `faq` | Questions fréquentes |
| `stats` | Chiffres clés |
| `team` | Présentation de l'équipe |
| `cta` | Call to action |
| `text` | Texte libre |
| `video` | Intégration vidéo |

---

## 🔒 Sécurité production

```python
# settings.py (production)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 📧 Support

Pour toute question : support@siteforge.io
