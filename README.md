# Outbound Email Deliverability

Playbook to audit, harden, and operate outbound email so messages land in the primary inbox — not spam.

This repository turns the “Improve Outbound Email Deliverability Strategy and SMTP Setup” workstream into something you can implement and monitor.

## Objectives

| Goal | Target |
| --- | --- |
| Inbox placement | Near-100% delivery to the primary inbox for authenticated, opted-in mail |
| Authentication | SPF + DKIM (2048-bit) + DMARC on every sending domain |
| Alignment | From domain aligns with SPF or DKIM (preferably both) |
| Complaints | < 0.1% (hard ceiling 0.3% at Gmail) |
| Hard bounces | < 2% |
| Transit | TLS 1.2+ on every SMTP hop you control |
| Visibility | Google Postmaster Tools + Microsoft SNDS + blacklist alerts |

Google, Yahoo, and Microsoft treat SPF, DKIM, and DMARC as the floor for bulk senders (roughly 5,000+ messages/day). Missing records are rejected before anyone reads the subject line.

## What is in this repo

```
docs/            Strategy, DNS, SMTP, reputation, bounce handling, runbook
dns/             Copy-paste DNS records and a sender inventory schema
config/          Postfix, OpenDKIM, and TLS policy examples
scripts/         DNS, rDNS, blacklist, warmup, and bounce-suppression tools
inventory/       Sender and suppression-list templates
checklists/      Implementation checklist mapped to the original ticket
.github/         Daily deliverability GitHub Action + incident issue template
```

## Fast start

1. Copy `inventory/senders.yaml.example` → `inventory/senders.yaml` and list every system that sends as your domain (Workspace, SES, SendGrid, app servers, CRMs).
2. Publish **one** SPF record per sending domain. Stay under the 10-DNS-lookup limit.
3. Enable **2048-bit DKIM** on each sender and publish the selector TXT/CNAME records.
4. Publish DMARC at `p=none` with `rua`/`ruf` mailboxes. Collect reports for 2–4 weeks, then tighten to `p=quarantine` and later `p=reject`.
5. Confirm PTR / FCrDNS on every dedicated sending IP.
6. Register the domain in [Google Postmaster Tools](https://postmaster.google.com/) and [Microsoft SNDS](https://sendersupport.olc.protection.outlook.com/snds/).
7. Run the checks:

```bash
python3 scripts/check_dns.py example.com
python3 scripts/check_rdns.py 203.0.113.10
python3 scripts/check_blacklists.py 203.0.113.10 example.com
python3 scripts/warmup_schedule.py --days 28 --target-per-day 2000
```

8. Wire hard-bounce (5xx) and complaint events into `scripts/bounce_suppress.py` so those addresses never get another message.

Do not put production secrets, private keys, or live suppression lists in git. Use the `.example` files.

## Architecture (recommended)

```
Corporate domain (example.com)
  └── transactional + product mail   DMARC p=quarantine → p=reject

Outbound / marketing subdomain (mail.example.com or a sibling domain)
  └── campaigns, newsletters         separate IPs, own warmup, own DKIM

Dedicated sending IPs
  └── PTR = mail.example.com
  └── A   = same IP  (FCrDNS)
  └── TLS 1.2+ only
```

Keep cold or high-risk outreach off the corporate apex domain. Burn a subdomain, not the brand domain.

## SLOs

| Signal | Green | Yellow | Red |
| --- | --- | --- | --- |
| SPF / DKIM / DMARC pass rate | ≥ 99% | 95–99% | < 95% |
| Gmail domain reputation | High | Medium | Low |
| Spam complaint rate | < 0.1% | 0.1–0.3% | > 0.3% |
| Hard bounce rate | < 2% | 2–5% | > 5% |
| Blacklist listings | 0 | watchlist | Spamhaus / Barracuda / major RBL |
| TLS on outbound | 100% | — | any cleartext |

## Implementation order

The original ticket maps 1:1 to [checklists/implementation.md](checklists/implementation.md).

1. [DNS & authentication](docs/02-dns-authentication.md) — SPF, DKIM, DMARC
2. [SMTP & IP](docs/03-smtp-and-ip.md) — rDNS, warmup, TLS
3. [Reputation](docs/04-reputation-and-monitoring.md) — Postmaster, SNDS, RBLs
4. [Bounces & FBLs](docs/05-bounce-and-fbl.md) — suppression list
5. [Content & list hygiene](docs/06-content-and-list-hygiene.md)
6. [Ops runbook](docs/07-runbook.md)

## License

MIT. Templates are examples — replace placeholders before you publish DNS or open SMTP to the internet.
