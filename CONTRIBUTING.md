# Contributing

This repo is an operations playbook. Keep it boring and accurate.

- Do not commit DKIM private keys, SMTP passwords, or live suppression lists.
- Prefer concrete records and commands over vendor marketing.
- When a provider changes an `include:` name, update `docs/02-dns-authentication.md` and `inventory/senders.yaml.example` in the same change.
- Scripts stay dependency-light (`dnspython` only).
