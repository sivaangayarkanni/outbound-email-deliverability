# Bounce handling and feedback loops

A suppression list is the cheapest deliverability control you have. Every hard bounce or spam complaint that you re-mail trains the ISP that you ignore signals.

## Bounce classes

| Class | SMTP | Action |
| --- | --- | --- |
| Hard bounce | 5xx — user unknown, domain invalid | Suppress immediately. Never retry. |
| Soft bounce | 4xx — mailbox full, greylist, try later | Retry with exponential backoff for 24–72h, then suppress or park. |
| Block / policy | 5xx with “spam”, “blocked”, “policy” | Stop that campaign / IP. Do not treat as a bad address until confirmed. |
| Autoresponder | 2xx with vacation / OOO | Ignore. Not a bounce. |

Parse the **enhanced status code** when present (`5.1.1`, `5.7.1`, `4.2.2`). Do not regex the human text alone — it changes by provider.

## Feedback loops (FBL)

An FBL is how Gmail (via Postmaster), Yahoo, Microsoft (JMRP), and others tell you a recipient hit “Report spam.”

- Register every sending IP / domain with each FBL you can.
- The complaint event contains the original recipient (or a hashed identifier).
- Add that address to the suppression list the same day.
- Do not send “why did you unsubscribe?” follow-ups to complainers.

Gmail does not operate a classic ARF FBL the way Yahoo does. Use Postmaster spam-rate plus List-Unsubscribe compliance.

## One-click unsubscribe (marketing)

RFC 8058 headers, required in practice for bulk mail to Gmail/Yahoo:

```
List-Unsubscribe: <mailto:unsub@example.com?subject=unsub>, <https://example.com/unsub/TOKEN>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

Honor the POST within one business day. Process mailto as well.

Transactional mail (receipts, security codes) should **not** carry campaign unsubscribe headers.

## Suppression list

Store:

- address (normalized, lowercase local+domain; be careful with `+tag` — suppress the mailbox, not every tag, unless your system treats tags as distinct)
- reason (`hard_bounce`, `complaint`, `unsubscribe`, `manual`, `role_account`)
- source (campaign id, FBL name, SMTP code)
- timestamp
- expires_at (usually never for hard bounce / complaint)

`scripts/bounce_suppress.py` is a file-backed starter. Replace the backend with your ESP suppression API or a shared database before production volume.

## Role and trap addresses

Do not mail:

- `abuse@`, `postmaster@`, `spam@`, `noc@`, `security@`
- Purchased or scraped lists
- Addresses that have not engaged in 6–12 months (sunset policy)

Spam traps (pristine and recycled) are how lists get you listed on Spamhaus. The only defense is confirmed opt-in and aggressive sunset.

## Wiring an MTA

Postfix: pipe 5xx responses from logs (`postfix/smtp`) into the suppressor, or use a policy service.

ESP (SendGrid, SES, Mailgun, Postmark): subscribe to their bounce and complaint webhooks and call the same suppressor.

SES example event names: `Bounce` (permanent), `Complaint`. Drop `Delivery` / `Send`.
