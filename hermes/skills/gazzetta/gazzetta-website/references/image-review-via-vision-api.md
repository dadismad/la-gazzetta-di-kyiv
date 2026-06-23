# Image / Screenshot Review via Vision API

When the user sends a screenshot and the agent cannot use native vision tools, fall back to calling a multimodal LLM API directly. This is the reliable pattern when `vision_analyze` is unavailable, tesseract OCR is not installed, or the macOS version predates Vision framework support.

## Gemini Vision via API Key (Preferred Path)

Get a free API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (same Google account as GCS). Add to `~/.hermes/.env`:
```
GEMINI_API_KEY=AIza...
```

Then call the Gemini API directly — no GCP project, no Vertex AI, no billing needed:

```python
import base64, json, urllib.request, os

img_path = "/path/to/image.jpg"
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

# Read Gemini key from .env
api_key = None
env_path = os.path.expanduser(os.path.join("~", ".hermes", ".env"))
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if "GEMINI_API_KEY" in line and not line.startswith("#"):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in ~/.hermes/.env")

data = json.dumps({
    "contents": [{
        "parts": [
            {"text": "Describe this screenshot in detail. What do you see? Read all visible text."},
            {"inline_data": {"mime_type": "image/png", "data": img_b64}}
        ]
    }]
}).encode()

req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
    data=data,
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())
print(result["candidates"][0]["content"]["parts"][0]["text"])
```

**Rate limits:** 1,500 requests/day on free tier. More than enough for screenshot reviews.

**When NOT to use Gemini:**
- The API key isn't in `.env` — prompts the agent to guide the user to aistudio.google.com/apikey
- Quota exhausted — fall back to OpenAI or Anthropic patterns below

## OpenAI / Anthropic Patterns

- An API key for a vision-capable provider (OpenAI, Anthropic, Groq with vision access)
- Python 3 with `urllib` (stdlib, no pip installs needed)

## Proven Pattern

```python
import base64, json, urllib.request, os

img_path = "/path/to/image.jpg"
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

# Get API key from Hermes .env
api_key = None
env_path = os.path.expanduser(os.path.join("~", ".hermes", ".env"))
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if "OPENAI_API_KEY" in line:
            api_key = line.split("=", 1)[1].strip()
            break

data = json.dumps({
    "model": "gpt-4o-mini",  # cheapest vision-capable model
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "Describe this screenshot in detail. What app/page is shown? Read visible text."},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + img_b64}}
    ]}],
    "max_tokens": 500
}).encode()

req = urllib.request.Request(
    "https://api.openai.com/v1/chat/completions",
    data=data,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }
)
resp = urllib.request.urlopen(req, timeout=45)
result = json.loads(resp.read())
print(result["choices"][0]["message"]["content"])
```

## Provider Quirks

| Provider | Model | Vision Support | Notes |
|----------|-------|---------------|-------|
| **Google Gemini** | `gemini-2.0-flash` | ✅ | **PREFERRED.** Free tier: 1,500 req/day. Same Google account as GCS. No project setup needed. See Gemini section below. |
| OpenAI | `gpt-4o-mini` | ✅ | Cheapest. Rate-limited on free tier (429). |
| OpenAI | `gpt-4o` | ✅ | More reliable, higher cost. |
| Groq | `llama-3.2-90b-vision-preview` | ⚠️ | May return 403 if vision access not enabled on key. |
| DeepSeek | Any | ❌ | Does not support `image_url` content type. |
| Anthropic | `claude-3-haiku` | ✅ | Requires different API format. |
| **Vertex AI** | `gemini-2.0-flash` | ❌ | NOT viable. Requires full GCP project with AI Platform enabled. The Gazzetta project (`project-e5e0244c-b94d-41a1-810`) is GCS-only — all Gemini models return 404. Use the free API key path instead. |
| **GitHub Copilot CLI** | GPT-4o vision | ❌ | NOT viable on this machine. Binary compiled for macOS 13.5+ (user is on 11.7.4). Also requires Node 24+ (user has 22). |

## Quick Diagnosis Before Calling API

Use pixel sampling to guess image type before spending API credits:

```python
from PIL import Image
img = Image.open(img_path)
w, h = img.size
dark_pct = sum(1 for y in range(0,h,20) for x in range(0,w,20)
               if sum(img.getpixel((x,y))[:3])/3 < 128) / ((w//20)*(h//20)) * 100
# dark_pct > 60%: likely dark-theme console (GCP, terminal)
# dark_pct < 20%: likely light background (JSON file, text editor, white webpage)
```

## When Not to Use

- **Gemini API key not set up** → guide user to aistudio.google.com/apikey (free, 2 minutes). Do NOT attempt Vertex AI — the GCS project doesn't support it.
- **Groq returns 403 on all vision models** → vision access may not be provisioned on the API key. Fall back to Gemini or OpenAI.
- **OpenAI returns 429 quota exceeded** → the key is on the free tier and exhausted. Wait or use a different key.
- **User sends a file directly** → prefer direct file reading over screenshot OCR. Only use vision when the content is trapped in an image format.
- **Copilot CLI on macOS < 13.5** → won't work. Don't waste time installing; the native binary is compiled for a newer OS.

## Avoiding Heredoc Quoting Issues

When calling a vision API from the `terminal` tool, Python heredocs (`python3 << 'EOF'`) often break on string quoting inside the script (especially when parsing `.env` files with `startswith('OPENAI_API_KEY=')`). **Use `write_file` + `terminal python3 /path/script.py` instead, or use `execute_code` which handles Python natively without shell escaping.** The `execute_code` approach is preferred — `urllib` from stdlib works inside execute_code and avoids all shell quoting issues.

Example execute_code pattern:
```python
import base64, json, urllib.request, os

img_path = "/path/to/image.jpg"
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

# Read key from .env
api_key = None
env_path = os.path.expanduser(os.path.join("~", ".hermes", ".env"))
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if "OPENAI_API_KEY" in line:
            api_key = line.split("=", 1)[1].strip()
            break

data = json.dumps({
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "Describe this screenshot."},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + img_b64}}
    ]}],
    "max_tokens": 500
}).encode()

req = urllib.request.Request(
    "https://api.openai.com/v1/chat/completions",
    data=data,
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
)
resp = urllib.request.urlopen(req, timeout=45)
result = json.loads(resp.read())
print(result["choices"][0]["message"]["content"])
```
