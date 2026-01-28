#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gecmisi.com.tr API Flask Backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import hashlib
import base64
import time
import random
from datetime import datetime

try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.Hash import SHA256
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'pycryptodome'])
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.Hash import SHA256

app = Flask(__name__)
CORS(app)  # Tüm originlere izin ver


def solve_challenge(challenge_id, salt, difficulty):
    """Proof-of-work challenge'ı çözer"""
    nonce = 0
    prefix = '0' * difficulty
    
    while True:
        data = f"{salt}{nonce}"
        hash_result = hashlib.sha256(data.encode()).hexdigest()
        
        if hash_result.startswith(prefix):
            return nonce, hash_result
        
        nonce += 1


def generate_fingerprint():
    """Browser fingerprint oluşturur"""
    return format(random.randint(0x10000000, 0xffffffff), '08x')


def generate_mouse_data():
    """Timestamp oluşturur"""
    return str(int(time.time() * 1000))


def encrypt_with_public_key(public_key_pem, data):
    """Public key ile veriyi RSA-OAEP ile şifreler"""
    try:
        public_key = RSA.import_key(public_key_pem)
        cipher = PKCS1_OAEP.new(public_key, hashAlgo=SHA256)
        
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = json.dumps(data).encode('utf-8')
        
        encrypted = cipher.encrypt(data_bytes)
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        
        return encrypted_b64
    except Exception as e:
        print(f"Şifreleme hatası: {e}")
        return None


def get_price_history(ilan_no):
    """Gecmisi.com.tr API'sinden fiyat geçmişini çeker"""
    
    base_url = "https://gecmisi.com.tr/api"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
        'Accept': '*/*',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json',
        'Origin': 'https://gecmisi.com.tr',
        'Referer': 'https://gecmisi.com.tr/v2/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    session = requests.Session()
    
    try:
        # 1. Public key al
        timestamp = int(time.time() * 1000)
        public_key_response = session.get(
            f"{base_url}/get-public-key?t={timestamp}",
            headers=headers,
            timeout=10
        )
        public_key_response.raise_for_status()
        public_key_data = public_key_response.json()
        public_key_pem = public_key_data.get("publicKey")
        
        # 2. Challenge token al
        challenge_response = session.get(
            f"{base_url}/get-challenge",
            headers=headers,
            timeout=10
        )
        challenge_response.raise_for_status()
        challenge_data = challenge_response.json()
        
        challenge_id = challenge_data.get("challengeId")
        salt = challenge_data.get("salt")
        difficulty = challenge_data.get("difficulty", 4)
        
        # 3. Challenge çöz
        nonce, solution = solve_challenge(challenge_id, salt, difficulty)
        
        # 4. Payload oluştur
        fingerprint = generate_fingerprint()
        timestamp_str = generate_mouse_data()
        encrypted_mouse = encrypt_with_public_key(public_key_pem, timestamp_str)
        
        behavior = {
            "mouse": random.randint(500, 1500),
            "keys": random.randint(5, 30),
            "scroll": random.randint(50, 200),
            "isHuman": True
        }
        
        payload = {
            "query_ilan_no": ilan_no,
            "adblock_token": "whitelist-bypass",
            "encryptedMouseKey": encrypted_mouse,
            "fingerprint": fingerprint,
            "behavior": behavior,
            "pow_challenge": {
                "challengeId": challenge_id,
                "nonce": nonce,
                "solution": solution
            }
        }
        
        response = session.post(
            f"{base_url}/fiyat-gecmisi",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "message": response.text}
        
    except Exception as e:
        return {"success": False, "message": str(e)}


@app.route('/api/price-history', methods=['POST'])
def price_history():
    """API endpoint - İlan fiyat geçmişini döndürür"""
    try:
        data = request.get_json()
        ilan_no = data.get('ilanNo', '').strip()
        
        if not ilan_no:
            return jsonify({
                'success': False,
                'message': 'İlan numarası gereklidir'
            }), 400
        
        result = get_price_history(ilan_no)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
