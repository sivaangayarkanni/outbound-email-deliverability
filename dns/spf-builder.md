# SPF builder notes

Build one string. Validate lookup count before you publish.

```
v=spf1
  [ ip4:x.x.x.x ]*
  [ ip6:x ]*
  [ include:vendor ]*
  [ a / mx — avoid if you can; they cost lookups ]
  -all
```

## Lookup budget (max 10)

| Mechanism | Lookups |
| --- | --- |
| `ip4` / `ip6` | 0 |
| `include:` | 1 + whatever the included record does |
| `a` / `mx` | 1+ |
| `redirect=` | 1 + target |
| `exists:` | 1 |

Google’s `_spf.google.com` currently expands to several nested lookups. Count them. If you add Microsoft + SendGrid + Mailgun + HubSpot you will blow the budget.

## Flattening

If you exceed 10 lookups:

1. Drop unused vendors.
2. Replace an `include:` with the vendor’s current `ip4:` ranges (and calendar a review — ranges change).
3. Move some senders to a subdomain with its own SPF.
4. Use a maintained flattener only if you understand it will rewrite DNS when vendor ranges change.

## Soft vs hard fail

| Qualifier | Meaning | When |
| --- | --- | --- |
| `~all` | Soft fail | Inventory incomplete |
| `-all` | Hard fail | Inventory complete; DMARC reports clean |
| `?all` | Neutral | Do not use |
| `+all` | Pass everyone | Never |
