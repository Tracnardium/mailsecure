#!/bin/bash
# MailSécure — Script d'installation et de lancement
# Compatible PikaOS, Ubuntu, Debian et dérivés

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║         MailSécure — Démarrage           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Vérification Python ──
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 non trouvé. Installation..."
    sudo apt-get update -q && sudo apt-get install -y python3 python3-pip python3-venv
fi

# ── Environnement virtuel ──
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel Python..."
    python3 -m venv venv
fi

# ── Activation ──
source venv/bin/activate

# ── Installation des dépendances ──
echo "📥 Vérification des dépendances..."
pip install -q -r requirements.txt

# ── Lancement ──
echo ""
echo "✅ Tout est prêt !"
echo ""
echo "  ┌─────────────────────────────────────┐"
echo "  │  Ouvrez votre navigateur sur :      │"
echo "  │  👉  http://localhost:5000           │"
echo "  └─────────────────────────────────────┘"
echo ""
echo "  Pour arrêter l'application : Ctrl+C"
echo ""

python3 app.py
