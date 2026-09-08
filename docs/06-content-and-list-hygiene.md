# Content and list hygiene

Infrastructure gets you to the front door. Content and list quality decide the folder.

## List

- Confirmed (double) opt-in for marketing.
- Verify addresses before first send (syntax + MX + catch-all risk).
- Sunset: no open/click in 90–180 days → last-chance series → suppress.
- Never import a purchased list onto a warmed domain.
- Separate transactional recipients from marketing recipients in software, even if they are the same people.

## Content signals that still matter

- From name + address the user recognizes.
- Subject matches the body. No bait.
- One primary CTA. Few links. Host images on a domain that matches the brand.
- Real reply-to on the same domain (or a clearly related subdomain).
- Plain-text multipart alternative alongside HTML.
- Balanced text-to-image ratio. An image-only email looks like a phish.
- No URL shorteners on first-touch mail.
- Accurate physical mailing address on commercial mail (CAN-SPAM / local equivalents).

## Cadence

Consistency beats hero blasts. If you send 2,000 a day, do not send 0 for two weeks and 40,000 on a Friday.

## Seed and engagement

Early in warmup, send to people who will reply. A reply is a stronger signal than an open (opens are noisy after Apple MPP).

## What this repo will not do

It will not write your copy, pick your ESP, or guarantee inbox placement. It will keep the floor (auth, TLS, rDNS, suppression, monitoring) from being the reason you miss.
