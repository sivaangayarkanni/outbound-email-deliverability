# DNS and authentication

Publish these records on the **exact domain used in the visible From header**. Alignment is what DMARC checks.

## SPF

SPF answers: "is this connecting IP allowed to send for this domain?"

Rules that break production:

- Only **one** SPF TXT record per name. Two records = PermError.
- Maximum **10 DNS lookups** (`include`, `a`, `mx`, `redirect`, `exists`). Over 10 = PermError, treated as fail.
- Do not use `+all`. Start with `~all` (soft fail) while you inventory senders; move to `-all` (hard fail) once DMARC reports are clean.

### Starter records

Google Workspace + a dedicated MTA IP:

```
v=spf1 include:_spf.google.com ip4:203.0.113.10 -all
```

Workspace + Microsoft 365 + SendGrid:

```
v=spf1 include:_spf.google.com include:spf.protection.outlook.com include:sendgrid.net -all
```

Domain that must never send:

```
v=spf1 -all
```

### Audit steps

1. `dig TXT example.com +short` — count SPF records (must be 1).
2. List every vendor in `inventory/senders.yaml`.
3. Flatten or drop unused `include:` mechanisms if you approach 10 lookups.
4. Send a test to Gmail → Show original → SPF: PASS.

Common vendor includes:

| Vendor | Mechanism |
| --- | --- |
| Google Workspace | `include:_spf.google.com` |
| Microsoft 365 | `include:spf.protection.outlook.com` |
| SendGrid | `include:sendgrid.net` |
| Mailgun | `include:mailgun.org` |
| Amazon SES | `include:amazonses.com` |
| SparkPost / MessageBird | `include:sparkpostmail.com` |
| Postmark | `include:spf.mtasv.net` |
| Zoho | `include:zoho.com` |

Prefer `ip4:` / `ip6:` for servers you own. It costs zero lookups.

## DKIM

DKIM answers: "did this domain sign the message, and was the body/headers altered?"

- Use **2048-bit** RSA keys. 1024-bit is weak in 2026.
- One selector per sending system (`google`, `s1`, `ses2026`, `mta1`).
- Rotate keys at least annually, or immediately after a vendor change / suspected leak.
- Sign `From`, `To`, `Subject`, `Date`, `Message-ID`, `MIME-Version`, `Content-Type`.

### Record shape

```
Host:  s1._domainkey.example.com
Type:  TXT
Value: v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
```

Some ESPs give you CNAMEs instead of a public key. That is fine — publish exactly what they give you.

### Generate a 2048-bit key (self-hosted MTA)

```bash
opendkim-genkey -b 2048 -s s1 -d example.com
# publishes s1.txt  →  DNS
# private key s1.private → /etc/opendkim/keys/example.com/s1.private  (mode 600)
```

Never commit `*.private` or `*.pem`.

## DMARC

DMARC answers: "if SPF or DKIM fail alignment, what should the receiver do, and where do I get the report?"

Publish at `_dmarc.example.com`.

### Phase 0 — monitor (week 0)

```
v=DMARC1; p=none; rua=mailto:dmarc-reports@example.com; ruf=mailto:dmarc-forensics@example.com; fo=1; adkim=r; aspf=r; pct=100
```

Create the two mailboxes (or a dedicated parser). `rua` = aggregate XML daily. `ruf` = per-message forensic; many providers rate-limit or omit `ruf`.

### Phase 1 — quarantine (after 2–4 clean weeks)

```
v=DMARC1; p=quarantine; pct=25; rua=mailto:dmarc-reports@example.com; fo=1; adkim=s; aspf=s
```

Raise `pct` 25 → 50 → 100.

### Phase 2 — reject (corporate / transactional domain)

```
v=DMARC1; p=reject; pct=100; rua=mailto:dmarc-reports@example.com; adkim=s; aspf=s
```

`adkim=s` / `aspf=s` = strict alignment (From domain must exactly match the authenticated domain, not a parent). Use relaxed (`r`) until every vendor is aligned, then tighten.

### Alignment reminder

- SPF alignment: envelope MAIL FROM / Return-Path domain vs From header.
- DKIM alignment: d= domain on the signature vs From header.
- Passing SPF on a vendor bounce domain does **not** help DMARC unless you also pass aligned DKIM or aligned SPF.

## BIMI (optional)

Once DMARC is `p=quarantine` or `p=reject` at pct=100, you can add BIMI (brand logo in supporting inboxes). Requires a Verified Mark Certificate for Gmail. Not required for deliverability; skip until auth is boringly green.

## TTL

Use 300–3600 seconds while iterating. Raise to 3600–14400 after the records stabilize.

## Verification commands

```bash
dig TXT example.com +short
dig TXT s1._domainkey.example.com +short
dig TXT _dmarc.example.com +short
python3 scripts/check_dns.py example.com
```

External validators: MXToolbox, dmarcian, Google Admin Toolbox Check MX, mail-tester.com (one-off only).
