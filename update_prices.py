#!/usr/bin/env python3
import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime

CRYPTO_IDS = [
    'ethereum', 'binancecoin', 'solana', 'sui', 'mantra', 'near', 'sei-network',
    'gmx', 'floki', 'fetch-ai', 'aethir', 'aster-2', 'gains-network',
    'axie-infinity', 'layer3', 'rivalz-network', 'lingo', 'lumia',
    'my-lovely-coin', 'carv', 'bluwhale', 'zero-gravity', 'machina', 'pump-fun'
]

SYMBOLS = [
    'ETH', 'BNB', 'SOL', 'SUI', 'MANTRA', 'NEAR', 'SEI',
    'GMX', 'FLOKI', 'FET', 'ATH', 'ASTER', 'GNS',
    'AXS', 'L3', 'RIZ', 'LINGO', 'LUMIA',
    'MLC', 'CARV', 'BLUAI', '0g', 'MXNA', 'PUMP'
]

# Sanity check — blocca lo script se le liste sono disallineate
assert len(CRYPTO_IDS) == len(SYMBOLS), \
    f"ERRORE: CRYPTO_IDS ({len(CRYPTO_IDS)}) e SYMBOLS ({len(SYMBOLS)}) hanno lunghezze diverse!"

def fetch_prices():
    """Scarica prezzi da CoinGecko"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ','.join(CRYPTO_IDS),
        'vs_currencies': 'usd'
    }

    headers = {'accept': 'application/json'}
    api_key = os.environ.get('COINGECKO_API_KEY')
    if api_key:
        headers['x-cg-demo-api-key'] = api_key
    print(f"CoinGecko: {'con Demo API key' if api_key else 'SENZA API key (keyless)'}")

    # Fino a 5 tentativi: su 429 (rate limit) o 5xx aspetta e riprova
    for attempt in range(1, 6):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
        except requests.RequestException as e:
            print(f"Tentativo {attempt}: errore di rete: {e}")
            time.sleep(15 * attempt)
            continue

        print(f"Tentativo {attempt}: HTTP {response.status_code}")
        if response.status_code == 200:
            break
        if response.status_code == 429 or response.status_code >= 500:
            ra = response.headers.get('Retry-After', '')
            wait = min(int(ra), 120) if ra.isdigit() else 15 * attempt
            print(f"   Risposta: {response.text[:300]}")
            print(f"   Attendo {wait}s e riprovo...")
            time.sleep(wait)
            continue
        # Altri errori (401, 403, 400...): inutile riprovare
        print(f"   Risposta: {response.text[:500]}")
        sys.exit(1)
    else:
        print("❌ CoinGecko non ha risposto correttamente dopo 5 tentativi")
        sys.exit(1)

    data = response.json()
    missing = [i for i in CRYPTO_IDS if i not in data]
    if missing:
        print(f"⚠️  ID senza prezzo: {missing}")

    prices = {}
    for cg_id, symbol in zip(CRYPTO_IDS, SYMBOLS):
        if cg_id in data and 'usd' in data[cg_id]:
            prices[symbol] = data[cg_id]['usd']
        else:
            prices[symbol] = None

    return prices

def update_csv():
    """Aggiorna il CSV con i nuovi prezzi"""
    df = pd.read_csv('_Snapshots_WIDE.csv')

    # Blocca se CSV e SYMBOLS non coincidono (evita colonne create/abbandonate in silenzio)
    csv_cols = set(df.columns) - {'Data'}
    if csv_cols != set(SYMBOLS):
        print(f"❌ Colonne solo nel CSV: {sorted(csv_cols - set(SYMBOLS))}")
        print(f"❌ Simboli solo nello script: {sorted(set(SYMBOLS) - csv_cols)}")
        sys.exit(1)

    today = datetime.now().strftime('%d/%m/%Y')

    if today in df['Data'].values:
        print(f"⚠️  Data {today} già presente, skip aggiornamento")
        return

    prices = fetch_prices()

    new_row = {'Data': today}
    new_row.update(prices)

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv('_Snapshots_WIDE.csv', index=False)
    print(f"✅ Aggiornato: {today}")
    print(f"   Crypto aggiornate: {sum(1 for v in prices.values() if v is not None)}/{len(prices)}")

if __name__ == '__main__':
    update_csv()
