#!/usr/bin/env python3
import requests
import pandas as pd
from datetime import datetime

CRYPTO_IDS = [
    'ethereum', 'binancecoin', 'solana', 'sui', 'avalanche-2', 'celestia', 'mantra',
    'near', 'sei-network', 'arbitrum', 'gmx', 'floki', 'manta-network',
    'fetch-ai', 'notcoin', 'aethir', 'gala',
    'venom', 'foxy', 'shrapnel-2', 'coreum', 'aster-2', 'step-app-fitfi',
    'ultra', 'bitrise-token', 'natix-network', 'soil', 'senate', 'multibit',
    'terra-luna', 'tokenfi', 'gains-network', 'reserve-rights-token',
    'woo-network', 'axie-infinity', 'layer3', 'moonveil', 'rivalz-network',
    'lingo', 'lumia', 'zeus-network', 'sidus', 'my-lovely-coin', 'carv',
    'bluwhale', 'zero-gravity', 'machina'
]

SYMBOLS = [
    'ETH', 'BNB', 'SOL', 'SUI', 'AVAX', 'TIA', 'MANTRA', 'NEAR', 'SEI', 'ARB', 'GMX',
    'FLOKI', 'MANTA', 'FET', 'NOT', 'ATH', 'GALA', 'VENOM', 'FOXY', 'SHRAP',
    'COREUM', 'ASTER', 'FITFI', 'UOS', 'BRISE', 'NATIX', 'SOIL', 'SENATE',
    'MUBI', 'LUNC', 'TOKEN', 'GNS', 'RSR', 'WOO', 'AXS', 'L3', 'MORE', 'RIZ',
    'LINGO', 'LUMIA', 'ZEUS', 'SIDUS', 'MLC', 'CARV', 'BLUAI', '0g', 'MXNA'
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

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

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
