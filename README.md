# 🚀 SiteForge — CMS No-Code avec Django

Plateforme complète de création de sites web no-code, avec éditeur drag & drop, domaines personnalisés et abonnements Stripe.


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



## 📧 Support

Pour toute question : support@siteforge.io
