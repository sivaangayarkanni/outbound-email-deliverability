# Deliverability strategy

Inbox placement is a reputation problem dressed as an infrastructure problem. Authentication gets you accepted. Reputation, list quality, and consistent volume decide whether you land in the inbox.

## Principles

1. **Authenticate everything.** SPF, DKIM (2048-bit), DMARC. No exceptions for “just this CRM.”
2. **One identity per purpose.** Transactional mail and promotional mail should not share IPs or, if volume is high, even domains.
3. **Never surprise an ISP.** Sudden volume spikes look like a compromised server.
4. **Suppress immediately.** Hard bounces (5xx) and spam complaints never get a second chance.
5. **Measure the inbox, not the SMTP 250.** “Accepted by the MX” is not “seen by a human.”
6. **Enforce TLS you control.** TLS 1.2 minimum; prefer 1.3. Disable SSLv3 / TLS 1.0 / 1.1.

## Domain layout

| Domain | Use | DMARC end-state |
| --- | --- | --- |
| `example.com` | People, Workspace, invoices, password resets | `p=reject` |
| `mail.example.com` or sibling brand domain | Newsletters / outbound campaigns | `p=quarantine` then `p=reject` |
| Parked / unused domains | Nothing | `p=reject` + empty SPF (`v=spf1 -all`) so they cannot be spoofed |

## 2026 provider floor

- Gmail / Yahoo: bulk senders need SPF + DKIM + DMARC (at least `p=none` with reporting), one-click unsubscribe for marketing, complaint rate under 0.3%.
- Microsoft: similar bulk-sender bar; watch SNDS filter rates and sudden volume.
- Target complaint rate internally at **0.1%**, not 0.3%. Damage starts before the hard cap.

## What “near-100% inbox” actually means

You will not hit 100% to every mailbox on earth. Aim for:

- Authenticated transactional mail to engaged users: 98%+ inbox
- Permissioned marketing to a cleaned list: 90%+ inbox at Gmail/Yahoo, higher on well-warmed IPs
- Cold outreach: treat as a separate product with much lower daily caps and its own domains

If you need cold outbound, do not run it from the same domain that sends invoices.

## Ownership

| Area | Owner |
| --- | --- |
| DNS records (SPF/DKIM/DMARC/PTR requests) | Infra / IT |
| SMTP / MTA config, TLS, queues | Infra |
| List hygiene, suppression, unsub | Product / Growth |
| Content, cadence, warmup calendar | Whoever presses send |
| Incident response | On-call + the sending team |

## Success criteria for this project

- [ ] Every sending domain has exactly one SPF record and it authorizes every live sender
- [ ] Every sender signs with 2048-bit DKIM; selectors documented
- [ ] DMARC published, reports arriving, policy path agreed (`none` → `quarantine` → `reject`)
- [ ] Dedicated IPs have matching PTR and A records (FCrDNS)
- [ ] TLS 1.2+ enforced on the outbound MTA
- [ ] Postmaster Tools + SNDS enrolled
- [ ] Blacklist monitor running on a schedule
- [ ] Hard bounces and FBL complaints auto-suppress
