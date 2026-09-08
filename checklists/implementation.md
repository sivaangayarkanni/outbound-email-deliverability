# Implementation checklist

Mapped to the original ticket. Check items off in GitHub Issues as you complete them.

## 1. DNS and authentication

- [ ] Inventory every system that sends as the domain (`inventory/senders.yaml`)
- [ ] Audit existing TXT records — one SPF only
- [ ] Include every authorized IP and third party (Workspace, SES, SendGrid, Mailgun, …)
- [ ] SPF lookup count ≤ 10
- [ ] Policy `~all` while inventorying, then `-all`
- [ ] Generate 2048-bit DKIM keys (or enable vendor DKIM)
- [ ] Publish selector TXT/CNAME records
- [ ] Configure the MTA / ESP to sign with those selectors
- [ ] Create `dmarc-reports@` and `dmarc-forensics@` mailboxes
- [ ] Publish DMARC `p=none` with `rua` and `ruf`
- [ ] Confirm Gmail “Show original” shows SPF PASS, DKIM PASS, DMARC PASS
- [ ] After 2–4 clean weeks, raise DMARC to `p=quarantine` then `p=reject`

## 2. SMTP server and IP

- [ ] PTR for each dedicated sending IP points at the mail hostname
- [ ] Mail hostname A/AAAA record points back at that IP (FCrDNS)
- [ ] EHLO hostname is that same FQDN
- [ ] Warmup calendar generated and shared (`scripts/warmup_schedule.py`)
- [ ] Volume caps enforced in the ESP or MTA
- [ ] TLS 1.2+ on submission; outbound TLS enabled and logged
- [ ] Certificate auto-renewal for `mail.example.com`
- [ ] Port 587/465 for apps; port 25 only for MTA-to-MTA

## 3. Deliverability and reputation

- [ ] Domain registered in Google Postmaster Tools
- [ ] Dedicated IPs enrolled in Microsoft SNDS
- [ ] JMRP / Yahoo FBL enrolled where applicable
- [ ] Baseline blacklist check (Spamhaus, Barracuda, …)
- [ ] Scheduled blacklist monitor (`.github/workflows/deliverability-check.yml`)
- [ ] Hard-bounce pipeline writes to the suppression list
- [ ] Complaint / FBL pipeline writes to the suppression list
- [ ] Marketing mail has working one-click List-Unsubscribe

## 4. Sign-off

- [ ] SLOs from the README are on a dashboard or weekly review
- [ ] Runbook owners named
- [ ] DKIM private keys stored outside git
