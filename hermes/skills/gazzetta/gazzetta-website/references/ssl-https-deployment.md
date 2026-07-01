# SSL / HTTPS Deployment for GCS Custom Domain

## Problem
GCS buckets with custom domains (e.g., `www.lagazzettadikyiv.com` via CNAME → `c.storage.googleapis.com`) do NOT serve HTTPS. Browsers return `ERR_CERT_COMMON_NAME_INVALID`. The GCS direct URL (`storage.googleapis.com/www.lagazzettadikyiv.com`) works fine because it uses Google's wildcard cert.

## Fix: Google Cloud HTTPS Load Balancer + Managed Certificate

### Prerequisites
- `gcloud` SDK installed and authenticated (`~/lagazzettadikyiv/google-cloud-sdk/bin/gcloud`)
- Cloud DNS zone managing the domain (or access to DNS provider)
- GCP project with billing enabled

### Deployment Recipe

```bash
# 1. Reserve global static IP
gcloud compute addresses create gazzetta-lb-ip --global
IP=$(gcloud compute addresses describe gazzetta-lb-ip --global --format="value(address)")

# 2. Create backend bucket pointing to GCS bucket
gcloud compute backend-buckets create gazzetta-backend \
  --gcs-bucket-name=www.lagazzettadikyiv.com

# 3. Create URL map routing to backend bucket
gcloud compute url-maps create gazzetta-url-map \
  --default-backend-bucket=gazzetta-backend

# 4. Create managed SSL certificate (auto-renews)
gcloud compute ssl-certificates create gazzetta-ssl-cert \
  --domains=www.lagazzettadikyiv.com --global

# 5. Create target HTTPS proxy
gcloud compute target-https-proxies create gazzetta-https-proxy \
  --url-map=gazzetta-url-map --ssl-certificates=gazzetta-ssl-cert

# 6. Create forwarding rule (port 443)
gcloud compute forwarding-rules create gazzetta-https-rule \
  --address=gazzetta-lb-ip --global \
  --target-https-proxy=gazzetta-https-proxy --ports=443

# 7. Update DNS: change CNAME → A record pointing to LB IP
# If using Google Cloud DNS:
gcloud dns record-sets delete www.lagazzettadikyiv.com. \
  --type=CNAME --zone=lagazzettadikyiv
gcloud dns record-sets create www.lagazzettadikyiv.com. \
  --type=A --ttl=300 --rrdatas=$IP --zone=lagazzettadikyiv
```

## Adding a New Domain to an Existing Certificate (v23.22 — Field-Validated)

**Google-managed SSL certificates CANNOT be modified after creation** — you cannot add domains to an existing cert. Two approaches:

### Approach A: Create New Cert + Swap (Zero Downtime) ✅ VERIFIED v23.22

```bash
# 1. Create a NEW cert with ALL domains (old + new)
gcloud compute ssl-certificates create gazzetta-ssl-cert-v2 \
  --domains=www.lagazzettadikyiv.com,lagazzettadikyiv.com --global

# 2. WAIT for provisioning (10-30 min). Check status:
gcloud compute ssl-certificates describe gazzetta-ssl-cert-v2 \
  --format="json(managed.domainStatus)"

# 3. ONCE ACTIVE on ALL domains, swap the proxy:
gcloud compute target-https-proxies update gazzetta-https-proxy \
  --ssl-certificates=gazzetta-ssl-cert-v2 --global

# 4. Delete old cert:
gcloud compute ssl-certificates delete gazzetta-ssl-cert --global --quiet
```

### Approach B: Delete + Recreate (Causes Downtime If Not Careful)

**DO NOT USE approach B unless you accept SSL downtime.** The process:
1. Delete old cert → SSL broken
2. Create new cert → PROVISIONING (10-30 min)
3. Wait → site is down during provisioning

The safest path is Approach A: create new cert, wait, swap, then delete old.

## CRITICAL PITFALL: Swapping to PROVISIONING Cert Takes Site Down

If you update the HTTPS proxy to use a cert that is still PROVISIONING, the site goes down IMMEDIATELY with `ERR_CONNECTION_CLOSED`. The old cert is still ACTIVE but no longer referenced by the proxy.

**Fix if this happens:**
```bash
# Revert proxy to old ACTIVE cert immediately
gcloud compute target-https-proxies update gazzetta-https-proxy \
  --ssl-certificates=gazzetta-ssl-cert --global
# Wait 15s for propagation
sleep 15
curl -sI https://www.lagazzettadikyiv.com/
```

The old cert continues to serve www traffic while the new cert provisions. Only swap once the new cert shows ACTIVE for ALL domains.

## HTTP → HTTPS Redirect (Bare Domain Support)

For bare domain (`lagazzettadikyiv.com` without www) to work, you need an HTTP forwarding rule on port 80. Without this, `http://lagazzettadikyiv.com/` returns nothing.

```bash
# 1. Create HTTP target proxy on same URL map
gcloud compute target-http-proxies create gazzetta-http-proxy \
  --url-map=gazzetta-url-map --global

# 2. Create HTTP forwarding rule (same IP, port 80)
gcloud compute forwarding-rules create gazzetta-http-rule \
  --load-balancing-scheme=EXTERNAL --global \
  --target-http-proxy=gazzetta-http-proxy --ports=80 \
  --address=<LB_IP_ADDRESS>

# 3. Make sure the SSL cert includes the bare domain as a SAN
# (see Approach A above — add lagazzettadikyiv.com to domains)
```

### Verification
```bash
# Check cert status (PROVISIONING → ACTIVE within 15-30min)
gcloud compute ssl-certificates describe gazzetta-ssl-cert \
  --global --format="json(managed.status,managed.domainStatus)"

# Test HTTPS access
curl -sI https://www.lagazzettadikyiv.com/

# Test bare domain HTTP (should return 200)
curl -sI http://lagazzettadikyiv.com/

# Test bare domain HTTPS (only after cert provisions with bare domain SAN)
curl -sI https://lagazzettadikyiv.com/

# Verify DNS propagation
dig +short www.lagazzettadikyiv.com A
dig +short lagazzettadikyiv.com A
```

### Pitfall: DNS Propagation Delay
The old CNAME record may be cached (TTL 300s). After changing to A record, wait 5-10min for propagation. SSL cert provisioning requires Google to verify domain ownership at the new IP — this takes 10-30min after DNS propagates.

### Cost
~$18/mo for load balancer + $0.008/GB data transfer. First 5 forwarding rules free.
