<<<<<<< HEAD
# MailSécure 🛡️

Application web locale pour nettoyer et sécuriser sa boîte Gmail.
Fonctionne sur **PikaOS, Ubuntu, Debian** et tous les systèmes Linux.

---

## ⚡ Installation en 2 étapes

### 1. Ouvrez un terminal dans ce dossier et lancez :
```bash
chmod +x lancer.sh
./lancer.sh
```

### 2. Ouvrez votre navigateur sur :
```
http://localhost:5000
```

---

## 🔑 Connexion Gmail — Mot de passe d'application

Gmail **n'accepte pas** votre mot de passe habituel pour les connexions IMAP.
Vous devez créer un **mot de passe d'application** (gratuit, 2 minutes) :

1. Allez sur → https://myaccount.google.com/apppasswords
2. Sélectionnez "Autre (nom personnalisé)" → tapez "MailSécure"
3. Copiez les 16 caractères générés
4. Utilisez-les dans l'écran de connexion de l'app

> ⚠️ Si vous n'avez pas l'option "Mots de passe d'application", activez d'abord la **validation en deux étapes** sur votre compte Google.

---

## 🔒 Confidentialité

- Tout fonctionne **en local sur votre machine**
- Aucune donnée n'est envoyée à des serveurs externes
- La connexion IMAP se fait directement entre votre ordinateur et Gmail
- Votre mot de passe d'application est stocké **uniquement en session** (disparaît à la fermeture)

---

## 🛠 Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| **Analyse IMAP** | Scan de vos 200 derniers mails en temps réel |
| **Tri automatique** | Newsletters, Spam, Importants, Autres |
| **Suppression en masse** | Sélection manuelle + confirmation obligatoire |
| **Détection expéditeurs** | Liste de toutes les entreprises qui vous ont écrit |
| **Demande RGPD** | Génération + envoi d'email conforme Art. 17 |
| **Vérification fuites** | Intégration Have I Been Pwned |
| **Historique** | Suivi de toutes les demandes envoyées |

---

## 📋 Prérequis

- Python 3.8+ (pré-installé sur PikaOS)
- Connexion Internet
- Compte Gmail avec IMAP activé

### Activer IMAP sur Gmail :
Paramètres Gmail → Voir tous les paramètres → Transfert et POP/IMAP → Activer IMAP

---

## ❓ Problèmes fréquents

**"Identifiants incorrects"**
→ Utilisez bien le mot de passe d'application (16 caractères), pas votre mot de passe Google habituel.

**"Erreur de connexion"**
→ Vérifiez que l'IMAP est activé dans les paramètres Gmail.

**Port 5000 déjà utilisé**
→ Modifiez la dernière ligne de `app.py` : `port=5001`

---

*MailSécure — Application locale, open source, sans tracking.*
=======
# mailsecure
Application web locale pour nettoyer et sécuriser sa boîte Gmail. Fonctionne sur tous les systèmes Linux.
>>>>>>> 8b21b7106b16c062a362cda6043d043875711faa
