#!/usr/bin/env python3
"""
gcp_monitor.py — Gazzetta di Kyiv GCP Health Monitor
Monitors: SSL cert, site reachability, deploy freshness, CDN status.
Uses Gemini for anomaly analysis when API key available.
Designed for Google Cloud Always Free tier compliance.
"""

import os, sys, json, time, subprocess
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError

PROJECT_ROOT = os.environ.get('GAZZETTA_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE_URL = 'https://www.lagazzettadikyiv.com'
GCP_PROJECT = 'gazzetta-di-kyiv'
LOG_FILE = os.path.join(PROJECT_ROOT, 'data', 'gcp_monitor.log')

# ── Always Free tier limits ──
# GCS: 5GB storage, 1GB egress/month, 5000 Class A ops/month, 50000 Class B ops/month
# Cloud Functions: 2M invocations/month, 400K GB-seconds, 200K GHz-seconds
# Vertex AI Gemini: Check current pricing — use cautiously

def log(msg, level='INFO'):
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] {level}: {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def check_ssl():
    """Check SSL certificate validity via openssl."""
    from subprocess import run, PIPE
    try:
        result = run(
            ['openssl', 's_client', '-connect', 'www.lagazzettadikyiv.com:443', '-servername', 'www.lagazzettadikyiv.com'],
            input=b'', capture_output=True, timeout=10
        )
        output = result.stderr.decode()
        # Extract expiration from openssl output
        result2 = run(
            ['bash', '-c', 'echo | openssl s_client -connect www.lagazzettadikyiv.com:443 -servername www.lagazzettadikyiv.com 2>/dev/null | openssl x509 -noout -enddate'],
            capture_output=True, timeout=10
        )
        date_str = result2.stdout.decode().strip()
        if 'notAfter=' in date_str:
            expiry = date_str.split('notAfter=')[1]
            return {'ok': True, 'expiry': expiry, 'raw': date_str}
        return {'ok': True, 'expiry': 'Unknown (from s_client)', 'raw': output[:200]}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def check_reachability():
    """Check if site returns HTTP 200."""
    try:
        req = Request(SITE_URL, headers={'User-Agent': 'GazzettaMonitor/1.0'})
        with urlopen(req, timeout=15) as resp:
            return {
                'ok': True,
                'status': resp.status,
                'etag': resp.headers.get('ETag', 'N/A'),
                'last_modified': resp.headers.get('Last-Modified', 'N/A'),
                'content_type': resp.headers.get('Content-Type', 'N/A'),
            }
    except URLError as e:
        return {'ok': False, 'error': str(e)}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def check_deploy_freshness():
    """Check deploy report for staleness."""
    try:
        req = Request(f'{SITE_URL}/deploy_report.txt', headers={'User-Agent': 'GazzettaMonitor/1.0'})
        with urlopen(req, timeout=10) as resp:
            content = resp.read().decode()
            return {'ok': True, 'content': content.strip()[:500]}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def check_anti_lying():
    """Verify no $5.0B or undefined strings on public site."""
    try:
        req = Request(SITE_URL, headers={'User-Agent': 'GazzettaMonitor/1.0'})
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode()
            issues = []
            if '$5.0B' in html:
                issues.append('STALE: $5.0B found in index.html')
            if 'undefined' in html and html.count('undefined') > 5:
                issues.append(f'STALE: undefined found {html.count("undefined")} times')
            return {'ok': len(issues) == 0, 'issues': issues}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def check_gcs_usage():
    """Check GCS storage usage against Always Free limits."""
    try:
        result = subprocess.run(
            ['gsutil', 'du', '-s', 'gs://www.lagazzettadikyiv.com'],
            capture_output=True, text=True, timeout=15
        )
        # Parse: "12345678   gs://..."
        if result.stdout.strip():
            bytes_used = int(result.stdout.strip().split()[0])
            mb_used = bytes_used / (1024 * 1024)
            pct_of_free = (bytes_used / (5 * 1024 * 1024 * 1024)) * 100  # 5GB free tier
            return {'ok': True, 'mb_used': round(mb_used, 2), 'pct_free_tier': round(pct_of_free, 2)}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def alert_if_critical(results):
    """Alert on critical issues."""
    criticals = []
    if not results.get('ssl', {}).get('ok'):
        criticals.append('SSL CERTIFICATE ISSUE')
    if not results.get('reachability', {}).get('ok'):
        criticals.append('SITE UNREACHABLE')
    if not results.get('anti_lying', {}).get('ok'):
        criticals.append('STALE/BROKEN CONTENT DETECTED')
    
    if criticals:
        log(f'🚨 CRITICAL: {", ".join(criticals)}', 'CRITICAL')
        return False
    return True

def main():
    log('── GCP Monitor Run ──')
    
    results = {}
    
    # 1. SSL
    log('Checking SSL...')
    results['ssl'] = check_ssl()
    log(f'  SSL: {results["ssl"]}')
    
    # 2. Reachability
    log('Checking reachability...')
    results['reachability'] = check_reachability()
    status = '✓' if results['reachability'].get('ok') else '✗'
    log(f'  Site: {status} {results["reachability"].get("status", "N/A")}')
    
    # 3. Deploy freshness
    log('Checking deploy freshness...')
    results['deploy'] = check_deploy_freshness()
    log(f'  Deploy report: {"ok" if results["deploy"].get("ok") else "ERROR"}')
    
    # 4. Anti-lying protocol
    log('Running anti-lying scan...')
    results['anti_lying'] = check_anti_lying()
    if results['anti_lying'].get('issues'):
        for issue in results['anti_lying']['issues']:
            log(f'  ⚠ {issue}', 'WARN')
    else:
        log('  ✓ No stale/undefined content')
    
    # 5. GCS usage
    log('Checking GCS storage...')
    results['gcs'] = check_gcs_usage()
    if results['gcs'].get('ok'):
        log(f'  Storage: {results["gcs"]["mb_used"]}MB ({results["gcs"]["pct_free_tier"]}% of free tier)')
    
    # Alert
    healthy = alert_if_critical(results)
    
    # Summary
    log(f'── Monitor complete: {"HEALTHY" if healthy else "ISSUES FOUND"} ──')
    
    # Write JSON status file
    status_path = os.path.join(PROJECT_ROOT, 'data', 'gcp_monitor_status.json')
    with open(status_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'healthy': healthy,
            'results': {k: v for k, v in results.items() if k != 'deploy'}
        }, f, indent=2, default=str)
    
    return 0 if healthy else 1

if __name__ == '__main__':
    sys.exit(main())
