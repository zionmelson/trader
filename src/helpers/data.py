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
      
async def filter_leverage_exchanges():
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
            # pattern: features['spot'] = {'leverage': True}
            if isinstance(feats.get('spot'), dict) and feats['spot'].get('leverage'):
               found = True
            # pattern: features has a dotted key 'spot.leverage'
            if feats.get('spot.leverage'):
               found = True
            # pattern: features['has'] may contain nested info
            if isinstance(feats.get('has'), dict):
               has_spot = feats['has'].get('spot')
               if isinstance(has_spot, dict) and has_spot.get('leverage'):
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

   print(f"Found {len(supported)} exchanges supporting spot.leverage")
   for e in supported:
      print(e)
      
async def filter_us_exchanges():
       us_exchanges = []
       for ex_id in ccxt.exchanges:
            cls = getattr(ccxt, ex_id, None)
            if cls is None:
                continue
            try:
                ex = cls()
            except Exception:
                continue

            try:
                # try a few common attribute names that exchanges use to indicate jurisdiction/country
                countries = (
                    getattr(ex, "countries", None)
                    or getattr(ex, "country", None)
                    or getattr(ex, "jurisdiction", None)
                    or getattr(ex, "jurisdictions", None)
                )

                def contains_us(val):
                    if val is None:
                        return False
                    if isinstance(val, (list, tuple, set)):
                        items = [str(x).upper() for x in val if x is not None]
                    else:
                        items = [str(val).upper()]
                    for it in items:
                        if it == "US" or it.startswith("US") or "UNITED" in it or "USA" in it:
                            return True
                        return False

                if contains_us(countries):
                    us_exchanges.append({"id": ex_id, "name": getattr(ex, "name", None), "countries": countries})
            finally:
                try:
                    await ex.close()
                except Exception:
                    pass

            for exchange in us_exchanges:
                print(exchange)