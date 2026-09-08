# Operations runbook

## Daily

1. Glance at Google Postmaster spam rate and domain reputation.
2. Glance at SNDS filter color if you own dedicated IPs.
3. Confirm the GitHub Action `deliverability-check` is green.
4. Drain bounce / complaint queues into the suppression list.

## Weekly

1. Open DMARC aggregate reports. Any new source sending as you? Any legitimate source failing?
2. Compare planned vs actual volume (warmup calendar).
3. Sample 10 messages in Gmail “Show original” — SPF/DKIM/DMARC PASS, aligned.

## Monthly

1. Re-inventory `inventory/senders.yaml` against reality (new SaaS tools love to send mail).
2. Check SPF lookup count.
3. Review DKIM selectors; retire dead ones after a grace period.
4. Rotate any self-hosted DKIM key older than 12 months.

## Incident: listed on a major blacklist

1. Freeze non-transactional sending on the listed IP/domain.
2. Capture the listing URL and reason code.
3. Check for open relay, compromised mailbox, form-spam, or a bad imported list.
4. Suppress the bad cohort.
5. Request delisting only after the cause is gone.
6. Resume on a warmup schedule, not at yesterday’s volume.

## Incident: Gmail reputation Low / complaint spike

1. Stop the campaign that is running.
2. Check List-Unsubscribe is present and working.
3. Check recent list sources (webinar import, event scan, partner file).
4. Cut daily volume 50% for 3–7 days.
5. Send only to 30-day engaged users until Postmaster recovers.

## Incident: DMARC reject blocking a real vendor

1. Do not immediately drop back to `p=none` unless business mail is down.
2. Identify the vendor from the aggregate report (`source IP`, `header from`, SPF/DKIM results).
3. Add their include / DKIM selector.
4. Wait for DNS TTL, then resend a test.
5. Document the vendor in `inventory/senders.yaml`.

## Incident: TLS or certificate expiry

1. Mail submission will fail if `smtpd_tls_security_level = encrypt` and the cert is dead.
2. Track `mail.example.com` certificate expiry in the same place you track public websites.
3. Prefer a short-lived ACME cert with auto-renew.

## Contacts to keep in the wiki

- DNS registrar / DNS host
- Cloud IP PTR request process
- ESP support + account ID
- Spamhaus request form
- Postmaster Tools owners (Google account list)
- On-call rotation
