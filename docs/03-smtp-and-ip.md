# SMTP server and IP optimization

## Reverse DNS (PTR) and FCrDNS

Receiving MTAs check that the connecting IP has a PTR, and that the PTR hostname resolves back to the same IP.

```
203.0.113.10  PTR  mail.example.com
mail.example.com  A   203.0.113.10
```

The PTR hostname should look like a mail server, not `ip-203-0-113-10.provider.example`. Ask the IP owner (cloud / colo / ISP) to set PTR — you usually cannot set it in your DNS panel.

```bash
python3 scripts/check_rdns.py 203.0.113.10
```

IPv6: same rule. If you advertise AAAA on the mail hostname, publish PTR on the v6 address too, or do not send over v6 yet.

## IP warmup

A new IP has no reputation. Blasting 50k messages on day one is how you land on Spamhaus.

Warm the **IP and the domain**. Engagement early (opens, replies, not-spam clicks) is the whole point.

### 28-day dedicated-IP schedule (transactional + opted-in)

| Day range | Daily cap (per IP) | Who gets mail |
| --- | --- | --- |
| 1–3 | 50–200 | Staff, seed accounts, most-engaged users |
| 4–7 | 200–500 | Recent purchasers / active accounts |
| 8–14 | 500–2,000 | Broader engaged cohort |
| 15–21 | 2,000–8,000 | Normal transactional + a slice of marketing |
| 22–28 | 8,000–target | Full planned volume if complaint/bounce stay green |

If any day: hard bounce > 2%, complaints > 0.1%, or Gmail reputation drops — **cut volume 50%** and hold for 3 days.

Generate a concrete calendar:

```bash
python3 scripts/warmup_schedule.py --days 28 --target-per-day 20000 --start 50
```

### Shared IP / ESP

You inherit the pool’s reputation. You still warm the **domain**. Start low, keep list clean, and do not onboard a purchased list.

### Shared vs dedicated

| | Shared ESP IP | Dedicated IP |
| --- | --- | --- |
| Best for | < ~50k/month, bursty | Steady high volume |
| Warmup | Domain only | Domain + IP, 2–4 weeks |
| Risk | Noisy neighbors | You own every mistake |

## TLS

Enforce TLS 1.2 or 1.3 on the listening submission port (587/465) and on outbound client connections.

Postfix sketch (full file in `config/postfix-main.cf.example`):

```
smtpd_tls_security_level = encrypt          # inbound submission
smtp_tls_security_level = may               # outbound; "encrypt" if every destination supports it
smtp_tls_protocols = >=TLSv1.2
smtpd_tls_protocols = >=TLSv1.2
smtpd_tls_mandatory_protocols = >=TLSv1.2
tls_preempt_cipherlist = yes
```

Disable EXPORT/NULL/RC4/3DES. Prefer ECDHE + AES-GCM / CHACHA20.

Test:

```bash
openssl s_client -starttls smtp -connect mail.example.com:587 -tls1_2
```

MTA-STS and TLS-RPT are inbound protections (others delivering to you). Add them when inbound mail matters; they do not replace outbound TLS.

## HELO / EHLO

EHLO hostname must be the FQDN that exists in DNS (`mail.example.com`), not `localhost` or a raw IP. Mismatch is a cheap spam signal.

## Rate limits and queues

- Cap concurrent connections per destination domain (Gmail in particular).
- Honor `421` / `450` deferrals — back off, do not retry immediately.
- Separate queues: transactional vs marketing, so a campaign cannot stall password resets.

## Ports

| Port | Use |
| --- | --- |
| 25 | MTA-to-MTA. Often blocked on cloud VMs; request an SMTP exception or relay through SES/SendGrid. |
| 587 | Submission with STARTTLS. Use this for apps and humans. |
| 465 | Implicit TLS submission. Fine as an alternative to 587. |

Applications should authenticate on 587/465. They should not speak open port 25 from random app nodes.
