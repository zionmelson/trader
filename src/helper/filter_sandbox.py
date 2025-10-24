# src/helper/filter_sandbox.py

import ccxt.async_support as ccxt

async def filter_sandbox_exchanges():
   supported = []
   for exchange_id in ccxt.exchanges:
      ex = None
      try:
         Exchange = getattr(ccxt, exchange_id)
         ex = Exchange({'enableRateLimit': True})
         feats = getattr(ex, 'features', {}) or {}

         found = False
         # common patterns: nested dicts or dotted key
         if isinstance(feats, dict):
            # pattern: features['spot'] = {'sandbox': True}
            if isinstance(feats.get('spot'), dict) and feats['spot'].get('sandbox'):
               found = True
            # pattern: features has a dotted key 'spot.sandbox'
            if feats.get('spot.sandbox'):
               found = True
            # pattern: features['has'] may contain nested info
            if isinstance(feats.get('has'), dict):
               has_spot = feats['has'].get('spot')
               if isinstance(has_spot, dict) and has_spot.get('sandbox'):
                  found = True

         if found:
            supported.append(exchange_id)
      except Exception:
         # ignore exchanges that fail to instantiate
         pass
      finally:
         if ex is not None:
            try:
               await ex.close()
            except Exception:
               pass

   print(f"Found {len(supported)} exchanges supporting spot.sandbox")
   for e in supported:
      print(e)