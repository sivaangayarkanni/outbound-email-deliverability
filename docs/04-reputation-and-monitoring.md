# Reputation and monitoring

## Google Postmaster Tools

1. Open https://postmaster.google.com/
2. Add every sending domain (apex and subdomains).
3. Prove ownership with the TXT record Google shows.
4. Wait for volume — dashboards stay empty until Gmail sees enough mail.

Watch:

- Domain reputation (High / Medium / Low)
- IP reputation
- Spam rate (stay under 0.1% internally)
- Auth rates (SPF, DKIM, DMARC)
- Encryption
- Delivery errors

Since late 2025 Gmail also exposes a compliance-style pass/fail view for bulk senders. Treat Fail as an incident.

## Microsoft SNDS

1. Open https://sendersupport.olc.protection.outlook.com/snds/
2. Request access for each dedicated sending IP.
3. Review daily: spam complaints, trap hits, filter result (green / yellow / red).

JMRP (Junk Mail Reporting Program) is Microsoft’s feedback loop. Enroll so Outlook user “junk” clicks become complaint events you can suppress.

## Yahoo / AOL

Enroll in Yahoo Complaint Feedback Loop where available. Keep one-click List-Unsubscribe on marketing mail.

## Blacklists

Check IPs and domains on a schedule, not only after a spike.

Priority lists:

- Spamhaus ZEN / CSS / DBL
- Barracuda
- SpamCop
- SORBS (noisy; investigate, do not panic)
- UCEPROTECT (often ignored by large inbox providers; still note it)
- Proofpoint / Cloudmark (via vendor portals)

```bash
python3 scripts/check_blacklists.py 203.0.113.10 example.com
```

If listed on Spamhaus:

1. Stop sending on that IP immediately.
2. Read the listing reason (exploit, snowshoe, volume, traps).
3. Fix the cause (open relay, harvested list, malware).
4. Request delisting only after the cause is gone.
5. Warm the IP or move traffic to a clean IP.

## Seed / inbox placement tests

Periodically send to a small panel of Gmail, Outlook, Yahoo, and corporate accounts you control. Record inbox vs spam. This is a sample, not a score — do not optimize copy solely to beat a seed test.

## Metrics cadence

| Cadence | What |
| --- | --- |
| Continuous | Bounce + complaint ingestion into the suppression list |
| Daily | Blacklist script (GitHub Action in this repo) |
| Daily | Postmaster spam rate + domain reputation |
| Weekly | DMARC aggregate report review |
| Monthly | DKIM key inventory, unused SPF includes, warmup vs actual volume |

## Alert thresholds

Page someone when:

- New listing on Spamhaus, Barracuda, or a major DBL
- Gmail domain reputation drops to Low
- Complaint rate ≥ 0.2% on a rolling day
- Hard bounce rate ≥ 5% on a campaign
- SPF/DKIM pass rate < 95%
- DMARC policy is `reject` and forensic/aggregate reports show a legitimate vendor failing
