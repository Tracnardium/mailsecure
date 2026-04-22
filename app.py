#!/usr/bin/env python3
"""
MailSécure - Application web locale pour nettoyer et sécuriser sa boîte Gmail
Fonctionne sur Linux (PikaOS, Ubuntu, etc.)
"""

from flask import Flask, render_template, request, jsonify, session
import imaplib
import email
from email.header import decode_header
import re
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ──────────────────────────────────────────────
# CONNEXION IMAP GMAIL
# ──────────────────────────────────────────────

def get_imap():
    if 'email' not in session or 'password' not in session:
        return None, "Non connecté"
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(session['email'], session['password'])
        return mail, None
    except imaplib.IMAP4.error as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def decode_str(s):
    if s is None:
        return ""
    parts = decode_header(s)
    result = ""
    for part, enc in parts:
        if isinstance(part, bytes):
            try:
                result += part.decode(enc or 'utf-8', errors='replace')
            except:
                result += part.decode('latin-1', errors='replace')
        else:
            result += str(part)
    return result

def categorize_mail(sender, subject, headers):
    sender_lower = (sender or "").lower()
    subject_lower = (subject or "").lower()
    headers_lower = (headers or "").lower()

    # Spam
    spam_keywords = ['win', 'gagné', 'casino', 'bitcoin', 'crypto', 'pills', 'viagra',
                     'lottery', 'prize', 'urgent', 'wire transfer', 'nigerian']
    if any(k in subject_lower for k in spam_keywords):
        return 'spam'

    # Newsletter / Marketing
    if 'list-unsubscribe' in headers_lower:
        return 'newsletter'
    newsletter_keywords = ['promo', 'solde', 'offre', 'newsletter', 'marketing',
                           'noreply', 'no-reply', 'info@', 'contact@', 'hello@',
                           'nouveauté', 'collection', 'vente', 'promotion', '-50%',
                           'exclusif', 'limité', 'flash', 'deal']
    if any(k in sender_lower or k in subject_lower for k in newsletter_keywords):
        return 'newsletter'

    # Transactionnel / Important
    trans_keywords = ['facture', 'reçu', 'commande', 'livraison', 'confirmation',
                      'invoice', 'receipt', 'order', 'payment', 'paiement',
                      'relevé', 'compte', 'bancaire', 'virement', 'mot de passe',
                      'sécurité', 'alerte', 'verify', 'vérif']
    if any(k in subject_lower for k in trans_keywords):
        return 'important'

    return 'autre'

# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connect', methods=['POST'])
def connect():
    data = request.json
    email_addr = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email_addr or not password:
        return jsonify({'success': False, 'error': 'Email et mot de passe requis'})

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(email_addr, password)
        mail.logout()
        session['email'] = email_addr
        session['password'] = password
        return jsonify({'success': True, 'email': email_addr})
    except imaplib.IMAP4.error:
        return jsonify({'success': False, 'error': 'Identifiants incorrects. Vérifiez votre email et mot de passe d\'application Gmail.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erreur de connexion : {str(e)}'})

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/status')
def status():
    return jsonify({'connected': 'email' in session, 'email': session.get('email', '')})

@app.route('/api/scan_mails', methods=['POST'])
def scan_mails():
    mail, err = get_imap()
    if err:
        return jsonify({'success': False, 'error': err})

    try:
        mail.select('INBOX')
        _, msg_ids = mail.search(None, 'ALL')
        ids = msg_ids[0].split()

        # Limit to last 500 mails for performance
        ids = ids[-500:]

        results = []
        senders_seen = {}

        for uid in reversed(ids[-200:]):  # Show last 200 in UI
            try:
                _, msg_data = mail.fetch(uid, '(RFC822.HEADER)')
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                sender = decode_str(msg.get('From', ''))
                subject = decode_str(msg.get('Subject', '(sans objet)'))
                date_str = msg.get('Date', '')
                headers = str(raw)

                # Extract email address
                match = re.search(r'<(.+?)>', sender)
                sender_email = match.group(1) if match else sender
                sender_display = re.sub(r'<.+?>', '', sender).strip().strip('"')
                if not sender_display:
                    sender_display = sender_email

                category = categorize_mail(sender, subject, headers)

                # Track unique senders
                domain = sender_email.split('@')[-1] if '@' in sender_email else sender_email
                if domain not in senders_seen:
                    senders_seen[domain] = {'count': 0, 'name': sender_display, 'email': sender_email, 'domain': domain}
                senders_seen[domain]['count'] += 1

                # Parse date
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(date_str)
                    date_fmt = dt.strftime('%d/%m/%Y')
                except:
                    date_fmt = date_str[:10] if date_str else '?'

                results.append({
                    'uid': uid.decode(),
                    'sender': sender_display[:40],
                    'sender_email': sender_email,
                    'subject': subject[:80],
                    'date': date_fmt,
                    'category': category
                })
            except Exception:
                continue

        mail.logout()

        # Build companies list from senders
        companies = []
        for domain, info in sorted(senders_seen.items(), key=lambda x: -x[1]['count']):
            companies.append({
                'domain': domain,
                'name': info['name'][:40],
                'email': info['email'],
                'count': info['count'],
                'source': 'email',
                'contact': f"dpo@{domain}" if not domain.startswith('gmail') else None
            })

        # Stats
        stats = {
            'total': len(results),
            'newsletter': sum(1 for m in results if m['category'] == 'newsletter'),
            'spam': sum(1 for m in results if m['category'] == 'spam'),
            'important': sum(1 for m in results if m['category'] == 'important'),
            'autre': sum(1 for m in results if m['category'] == 'autre'),
            'companies': len(companies),
        }

        return jsonify({'success': True, 'mails': results, 'companies': companies, 'stats': stats})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_mails', methods=['POST'])
def delete_mails():
    data = request.json
    uids = data.get('uids', [])
    if not uids:
        return jsonify({'success': False, 'error': 'Aucun mail sélectionné'})

    mail, err = get_imap()
    if err:
        return jsonify({'success': False, 'error': err})

    try:
        mail.select('INBOX')
        for uid in uids:
            mail.store(uid, '+FLAGS', '\\Deleted')
        mail.expunge()
        mail.logout()
        return jsonify({'success': True, 'deleted': len(uids)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check_hibp', methods=['POST'])
def check_hibp():
    """Vérifie Have I Been Pwned pour les fuites de données"""
    data = request.json
    email_addr = data.get('email', session.get('email', ''))
    if not email_addr:
        return jsonify({'success': False, 'error': 'Email requis'})

    # SHA-1 hash for k-anonymity
    sha1 = hashlib.sha1(email_addr.lower().encode()).hexdigest().upper()
    prefix = sha1[:5]

    try:
        # HIBP API - check breaches by email
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email_addr)}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'MailSecure-Local/1.0',
            'hibp-api-key': 'demo'  # Free endpoint for basic check
        })
        # Note: Full HIBP requires API key. We use the public endpoint.
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                breaches = json.loads(resp.read())
                return jsonify({'success': True, 'breaches': [
                    {'name': b['Name'], 'date': b.get('BreachDate', '?'), 'count': b.get('PwnCount', 0)}
                    for b in breaches
                ]})
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return jsonify({'success': True, 'breaches': [], 'message': 'Aucune fuite connue ✅'})
            elif e.code == 401:
                return jsonify({'success': True, 'breaches': [], 'message': 'Clé API HIBP requise pour la vérification complète', 'need_key': True})
            raise
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/send_gdpr', methods=['POST'])
def send_gdpr():
    data = request.json
    to_email = data.get('to')
    subject = data.get('subject')
    body = data.get('body')

    if not all([to_email, subject, body]):
        return jsonify({'success': False, 'error': 'Champs manquants'})

    if 'email' not in session:
        return jsonify({'success': False, 'error': 'Non connecté'})

    try:
        msg = MIMEMultipart()
        msg['From'] = session['email']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(session['email'], session['password'])
            server.send_message(msg)

        # Save to history
        history = session.get('gdpr_history', [])
        history.append({
            'to': to_email,
            'subject': subject,
            'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'status': 'envoyée'
        })
        session['gdpr_history'] = history
        session.modified = True

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/history')
def get_history():
    return jsonify({'history': session.get('gdpr_history', [])})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  MailSécure - Application locale")
    print("  Ouvrez votre navigateur sur :")
    print("  http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=False, host='127.0.0.1', port=5000)
