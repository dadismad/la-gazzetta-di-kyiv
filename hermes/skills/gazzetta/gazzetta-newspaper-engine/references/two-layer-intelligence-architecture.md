# Two-Layer Intelligence Architecture

Gazzetta di Kyiv uses a TWO-LAYER intelligence model to solve the amateur publisher problem: Alex is a newspaper publisher, not an engineer. When he describes what he wants, a single LLM interprets his words and builds things. But there's no second set of eyes to verify that interpretation was correct.

## The Problem

Alex says: "Make the site look professional."
Hermes builds: A desktop-first institutional layout.
Alex meant: "I want it to look good on phones because everyone reads via Telegram."

One LLM interpreting amateur words → one set of assumptions → costly rebuilding when assumptions are wrong.

## The Solution

```
ALEX (amateur publisher)
  │
  │ Voice messages, text
  ▼
┌─────────────────────────────────────────┐
│ LAYER 1: LOCAL HERMES (DeepSeek)        │
│                                         │
│ ROLE: Interpreter + Builder             │
│ - Understand what Alex wants            │
│ - Translate into technical work         │
│ - Write code, fix bugs, design          │
│ - Deploy to VM                          │
│ - NOT involved in production runs       │
└──────────────────┬──────────────────────┘
                   │
                   │ Code + interpretation
                   ▼
┌─────────────────────────────────────────┐
│ LAYER 2: CLOUD GOVERNOR (DeepSeek)        │
│                                         │
│ ROLE: Editorial Director + Ops Manager  │
│ - Reads Alex's original words           │
│ - Reads Hermes's interpretation         │
│ - Applies professional newspaper judgment│
│ - Can say: "Hermes misunderstood."      │
│ - Can say: "Correct build, but a real   │
│   newspaper would also do X."           │
│ - Runs production autonomously          │
│ - Reports to Alex on Telegram           │
└──────────────────┬──────────────────────┘
                   │
                   ▼
            PRODUCTION OUTPUT
       (site, Telegram, Reddit, X)
```

## Governor's Judgment Loop

Every cycle, the Governor evaluates:

1. **Alex's intent** (from voice/text) — what did the publisher actually want?
2. **Hermes's interpretation** — what did Layer 1 build?
3. **Editorial alignment** — does the output match Gazzetta's paradigm?
4. **Professional standards** — would a real financial newspaper do this?

If the Governor disagrees with Hermes's interpretation, it overrides and redirects. This prevents amateur misinterpretations from reaching production.

## Model Separation

| Layer | Model | Why |
|-------|-------|-----|
| Hermes (local) | DeepSeek | Code generation, debugging, rapid iteration |
| Governor (VM) | DeepSeek (ACTIVE) or Gemini (standby) | Editorial judgment, production management |
| Synthesis (VM) | DeepSeek Key 2 | Contradiction analysis, story generation |

**Current (June 2026):** Governor uses DeepSeek for the executive editor. Gemini was attempted but blocked by two issues: (1) prepaid credits depleted on the `AQ.` key, and (2) the Gemini API (`generativelanguage.googleapis.com`) rejects service account Bearer tokens necessary for GCP free-credit billing. Vertex AI (the GCP-native way to use Gemini) requires manual Terms of Service acceptance in console. DeepSeek works immediately with standard `sk-` Bearer auth and shares a key with the contradiction synthesis step (they don't run concurrently). If Gemini/Vertex AI becomes available, the governor can switch models by changing the `ask_*()` function call.
