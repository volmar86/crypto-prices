#!/usr/bin/env python3
import requests
import pandas as pd
from datetime import datetime

# Lista delle tue crypto (nell'ordine originale)
CRYPTO_IDS = [
    'ethereum', 'binancecoin', 'solana', 'avalanche-2', 'celestia', 'mantra-dao',
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
    'ETH', 'BNB', 'SOL', 'AVAX', 'TIA', 'OM', 'NEAR', 'SEI', 'ARB', 'GMX',
    'FLOKI', 'MANTA', 'FET', 'NOT', 'ATH', 'GALA', 'VENOM', 'FOXY', 'SHRAP',
    'COREUM', 'ASTER', 'FITFI', 'UOS', 'BRISE', 'NATIX', 'SOIL', 'SENATE',
    'MUBI', 'LUNC', 'TOKEN', 'GNS', 'RSR', 'WOO', 'AXS', 'L3', 'MORE', 'RIZ',
    'LINGO', 'LUMIA', 'ZEUS', 'SIDUS', 'MLC', 'CARV', 'BLUAI', '0g', 'MXNA'
]

def fetch_prices():
    """Scarica prezzi da CoinGecko"""
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ','.join(CRYPTO_IDS),
        'vs_currencies': 'usd'
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    # Mappa prezzi
    prices = {}
    for cg_id, symbol in zip(CRYPTO_IDS, SYMBOLS):
        if cg_id in data and 'usd' in data[cg_id]:
            prices[symbol] = data[cg_id]['usd']
        else:
            prices[symbol] = None
    
    return prices

def update_csv():
    """Aggiorna il CSV con i nuovi prezzi"""
    # Carica CSV esistente
    df = pd.read_csv('_Snapshots_WIDE.csv')
    
    today = datetime.now().strftime('%d/%m/%Y')
    
    # Controlla se oggi esiste già
    if today in df['Data'].values:
        print(f"⚠️  Data {today} già presente, skip aggiornamento")
        return
    
    # Scarica prezzi
    prices = fetch_prices()
    
    # Crea nuova riga
    new_row = {'Data': today}
    new_row.update(prices)
    
    # Aggiungi al dataframe
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Salva
    df.to_csv('_Snapshots_WIDE.csv', index=False)
    print(f"✅ Aggiornato: {today}")
    print(f"   Crypto aggiornate: {sum(1 for v in prices.values() if v is not None)}/{len(prices)}")

if __name__ == '__main__':
    update_csv()
