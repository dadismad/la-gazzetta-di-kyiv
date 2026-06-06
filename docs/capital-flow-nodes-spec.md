# Capital Flow Nodes — Specification & Architecture

## 1. Motivation

The existing Gazzetta di Kyiv capital-flow model tracks flat directional flows
(inflow/outflow, amount, sector, confidence). Each flow has a `flow_sources`
array listing origin sectors — but there is no **node decomposition**: no
distinction between source, destination, transit, or the structural adjacencies
that define how capital actually moves through the global financial system.

Professional trading desks (Goldman Sachs, Bridgewater, Point72) visualise
capital as a **network of nodes** with directional edges. The Fed Z.1 "Flow of
Funds" methodology decomposes the US economy into sectors with explicit
inter-sector lending/borrowing matrices. Bloomberg's CRPH (Capital Flow)
function and Refinitiv's Flow of Funds pages show source→destination edges
between node types.

This specification defines a **5-type node taxonomy** for Gazzetta's capital
flow visualization page, a JSON data model, and a pure-SVG/HTML/CSS
implementation with dark command-center aesthetics matching the Event Horizon
page.

## 2. Node Type Taxonomy

### 2.1 GOVERNMENTAL (type: `gov`)

| Field | Description |
|-------|-------------|
| **Sub-types** | Central banks (Fed, ECB, PBOC, BOJ), Sovereign wealth funds (Norges, ADIA, CIC, GPIF), Treasury departments, Government pension funds (CalPERS, G Fund), State-owned enterprises (CNPC, Rosneft), Defense procurement agencies |
| **Inbound sources** | Tax receipts, bond issuances (Treasuries, Bunds, JGBs), seigniorage, SWF oil/gas revenue allocations, pension contributions, special drawing rights (SDRs), central bank swap lines |
| **Outbound destinations** | Debt service (coupon payments), fiscal transfers (infrastructure, defense, welfare), QE asset purchases (MBS, Treasuries), FX reserve diversification (gold, EUR, CNY), SWF equity/debt/real asset deployment, state-directed lending (policy banks), defense procurement contracts |
| **Adjacent nodes** | ⇨ Corporate (bonds purchased by SWF/pension funds, defense contracts), ⇨ Institutional (pension fund flows into asset managers), ⇨ Retail (social security payments, tax refunds), ⇨ Crypto (CBDC issuance, seized asset auctions) |
| **Data sources** | Fed Z.1 (Tables F.1-F.125), IMF IFS, BIS International Banking Statistics, SWF annual reports, Treasury International Capital (TIC), central bank balance sheets |
| **Visual** | Rectangle node — dark slate (#1E293B) with gold (#D4AF37) left border. Icon: building/column glyph. Size proportional to total AUM/liabilities tracked |

### 2.2 PRIVATE / INSTITUTIONAL (type: `institutional`)

| Field | Description |
|-------|-------------|
| **Sub-types** | Hedge funds (Citadel, Bridgewater, Millennium), Mutual funds (Vanguard, BlackRock, Fidelity), Pension funds (CalPERS, CPPIB, ABP), Endowments (Harvard, Yale, Stanford), Family offices (ICM, Bezos Expeditions), Private equity (Blackstone, KKR, Apollo), Venture capital (a16z, Sequoia, Accel) |
| **Inbound sources** | LP contributions (pension fund allocations to PE/VC), 401k/IRA contributions into mutual funds, HNW family office inflows, institutional mandates (insurance general accounts), sovereign wealth fund FoF allocations, corporate buyback allocations to passive funds |
| **Outbound destinations** | Equity market purchases (IPO, secondary, block trades), fixed income purchases (corporate bonds, Treasuries, MBS), private company investments (VC/PE rounds), real estate & infrastructure debt/equity, derivative overlay (FX hedging, portfolio insurance), money market instruments |
| **Adjacent nodes** | ⇨ Corporate (VC funding, PE buyouts, equity issuance purchased), ⇨ Gov (Treasuries purchased, pension fund tax-exempt status), ⇨ Retail (mutual fund inflows from 401k), ⇨ Crypto (institutional crypto allocations, GBTC/EThe flows) |
| **Data sources** | EPFR Global fund flows (daily, weekly), Morningstar Direct (monthly AUM), SEC 13F filings (quarterly institutional holdings), Preqin (private capital), eVestment (mandate flows), Bloomberg FLOW function |
| **Visual** | Diamond-shaped node — slate (#1E293B) with blue (#3B82F6) left border. Icon: briefcase/portfolio glyph |

### 2.3 CRYPTO (type: `crypto`)

| Field | Description |
|-------|-------------|
| **Sub-types** | Centralized exchanges (Binance, Coinbase, Kraken, OKX), DeFi protocols (Uniswap, Aave, Lido, MakerDAO), Stablecoin issuers (Tether, Circle, Maker), Miners/stakers, DAO treasuries (Uniswap, ENS, Arbitrum), Bridge operators (Wormhole, LayerZero), Mixers/tumblers (Tornado Cash, Railgun), On-chain whale addresses |
| **Inbound sources** | Fiat on-ramps (bank transfers into CEX), Stablecoin minting (USDT/USDC issuance against fiat reserves), DeFi yield farming deposits, Mining block rewards (BTC issuance), DAO token sale revenues, Cross-chain bridge deposits, Institutional OTC desk fiat → crypto conversions |
| **Outbound destinations** | Fiat off-ramps (CEX → bank), Stablecoin redemption (USDT/USDC → fiat), CEX hot wallet → cold storage, DeFi withdrawal to L1, Cross-chain bridge outflows, Miner → CEX sell pressure, Mixer deposits (obfuscation), DAO treasury spending (grants, operations, liquidity mining) |
| **Adjacent nodes** | ⇨ Corporate (corporate treasury BTC holdings — MicroStrategy, Tesla), ⇨ Retail (retail on-ramps through Coinbase/Robinhood, 401k crypto exposure through 401k plan crypto options), ⇨ Institutional (GBTC, ETHE, futures-based ETFs, CME Bitcoin futures), ⇨ Gov (seized crypto auctions (USMS), CBDC research flows) |
| **Data sources** | CoinMetrics (on-chain exchange flows), Glassnode (exchange in/out, miner flows), DeFiLlama (TVL by chain/protocol), CoinGecko/CoinMarketCap volumes, Dune Analytics (custom on-chain queries), Chainalysis (illicit flows), CME/Deribit (institutional crypto derivatives) |
| **Visual** | Hexagon node — slate (#1E293B) with amber (#F59E0B) left border. Icon: blockchain/hex glyph |

### 2.4 CORPORATE (type: `corporate`)

| Field | Description |
|-------|-------------|
| **Sub-types** | Corporate treasuries (Apple, Microsoft, Google cash piles), Buyback programs (authorized share repurchases), M&A flows (cash/debt-funded acquisitions), Supply chain finance (PO financing, receivables factoring), Cross-border trade settlement (letter of credit, open account), Dividend payments, Corporate bond issuance, Commercial paper programs |
| **Inbound sources** | Operating cash flow (revenue minus expenses), Debt issuance (corporate bonds, CP, term loans), Equity issuance (IPO, follow-on, ATM), Tax refunds, government subsidies, Insurance settlement payouts, Asset sales (divestitures, spin-offs) |
| **Outbound destinations** | Share buybacks (equity → treasury stock), Dividend payments (cash → shareholders), M&A cash consideration (acquirer → target shareholders), Capex (buildings, equipment, R&D), Supply chain payments (payables, PO financing), Bond coupon & principal payments, Commercial paper rollover, Tax payments, Lobbying & political contributions |
| **Adjacent nodes** | ⇨ Institutional (buyback-driven passive flow into funds, VC/PE fundraising from corporate venture arms), ⇨ Gov (corporate tax payments, defense contracts, subsidy receipt), ⇨ Retail (dividends to retail shareholders, employee stock purchase plans), ⇨ Crypto (corporate BTC treasury, blockchain settlement pilots) |
| **Data sources** | SEC filings (10-K cash flow statements, 8-K buyback announcements), Dealogic/Refinitiv M&A database, S&P Global buyback data, Bloomberg corporate bond issuance calendar, Fed Z.1 Table F.103 (Nonfinancial Corporate Business), supply chain finance platforms (Prime Revenue, C2FO) |
| **Visual** | Rounded-square node — slate (#1E293B) with green (#10B981) left border. Icon: building/chart glyph |

### 2.5 RETAIL (type: `retail`)

| Field | Description |
|-------|-------------|
| **Sub-types** | 401k/IRA flows (Vanguard, Fidelity, Schwab retirement plans), Brokerage order flow (Robinhood, Schwab, E*Trade, Webull), Payment for order flow (PFOF) — Citadel Securities, Virtu Financial, Household savings reallocation (money market → equities, CDs → bonds), Margin debt, Cash savings deposits |
| **Inbound sources** | Payroll deductions (401k contributions), Direct bank transfers into brokerage accounts, Dividends & interest credited to brokerage cash, IRA/cash contributions, Margin loan drawdowns, Sale proceeds from other assets (real estate, business), Government stimulus/stimulus checks, Uninvested cash in sweep accounts |
| **Outbound destinations** | Retail equity purchases (common stock, ETFs), Retail options flow (PFOF routed to market makers), Mutual fund purchases (index funds, target date funds), Money market fund flows (cash parking), Bond purchases (Treasuries via TreasuryDirect, munis, corporate bonds via brokerage), Crypto on-ramp (Coinbase, Robinhood crypto), Bank deposit outflows (net new money into brokerages) |
| **Adjacent nodes** | ⇨ Institutional (401k → mutual fund flows, PFOF → market maker routing), ⇨ Corporate (dividend receipts, share purchases via buyback), ⇨ Crypto (retail on-ramp to CEX), ⇨ Gov (TreasuryDirect purchases, tax payments, I-bond purchases) |
| **Data sources** | ICI (Investment Company Institute) monthly fund flow survey, FINRA margin debt monthly, SEC Rule 605/606 order routing reports, Robinhood/Public quarterly metrics, Federal Reserve G.19 (consumer credit), FDIC deposit data, Census Bureau savings rate, Bureau of Economic Analysis (BEA) personal income |
| **Visual** | Circle node — slate (#1E293B) with violet (#A78BFA) left border. Icon: person/user glyph |

## 3. Fed Z.1 Methodology Mapping

The Federal Reserve's **Financial Accounts of the United States** (Z.1 release)
tracks the flow of funds between sectors of the US economy. The core concept is
the **Sources and Uses of Funds statement** for each sector:

```
For any sector: Net Lending (+) / Net Borrowing (-) =
    [Total Sources (What the sector receives)] 
  - [Total Uses (What the sector deploys)]
```

### Z.1 Sector Mapping to Gazzetta Nodes

| Z.1 Sector | Gazzetta Node Type | Key Z.1 Tables |
|------------|-------------------|----------------|
| Federal Government (S.131) | Gov | F.107 (Net borrowing), L.107 (debt outstanding) |
| State & Local Gov (S.131) | Gov | F.108, L.108 |
| Monetary Authority (S.121) | Gov | F.115 (Fed balance sheet) |
| Commercial Banks (S.121) | Institutional | F.111, L.111 |
| Money Market Funds (S.122) | Institutional | F.113, L.113 |
| Mutual Funds (S.123) | Institutional | F.114, L.114 |
| Pension Funds (S.124) | Institutional | F.117, L.117 |
| Nonfinancial Corporate Business (S.11) | Corporate | F.103, L.103 (debt securities) |
| Households & Nonprofit (S.14) | Retail | F.100 (household wealth), L.100 (mortgage debt) |
| Rest of the World (S.15) | Gov/Corporate | F.109, L.109 (cross-border) |

### Z.1 Matrix Form

The Z.1 publishes a **Sector-by-Asset matrix** every quarter showing:
- **Rows**: Source sectors (who provides the funding)
- **Columns**: Destination sectors (who receives the funding)
- **Cells**: Net flow ($B) between row and column

This is the conceptual model for Gazzetta's node adjacency matrix.

## 4. Professional Visualization Approaches

### Bloomberg Terminal — CRPH (Capital Flow Function)

- **Node-link diagram**: Central panel showing nodes as labeled boxes, edges as
  directional arrows color-coded by flow type (green = inflow, red = outflow)
- **Time scrubber**: Bottom slider to advance through quarters
- **Detail panel**: Right-side panel showing selected node's sources/uses
- **Heatmap mode**: Sector-by-sector matrix with cell shading for flow magnitude

### Refinitiv Eikon — Flow of Funds

- **Chord diagram**: Circular layout where each sector is an arc, flows between
  arcs are ribbons (width proportional to amount)
- **Sankey view**: 3-column layout (sources → channels → destinations) with
  proportional flow widths
- **Table view**: Raw matrix data sortable by magnitude

### Professional Trading Desk "War Room"

- **Force-directed graph**: Nodes arranged by proximity of connection strength
- **Highlight on hover**: Hovering a node highlights all connected edges, fades
  unconnected
- **Aggregation/decomposition**: Expand a node to see sub-types (e.g., expand
  "Institutional" to see "Hedge Funds", "Pension Funds", "Endowments")
- **Flow animation**: Animated particles moving along edges from source to
  destination

## 5. Data Model — JSON Schema

```jsonc
{
  "generated_at": "2026-06-07T00:00:00Z",
  "generated_by": "generate_flow_nodes.py",
  "update_frequency": "60m",
  "node_types": {
    "gov": { "label": "Governmental", "color": "#D4AF37" },
    "institutional": { "label": "Private/Institutional", "color": "#3B82F6" },
    "crypto": { "label": "Crypto", "color": "#F59E0B" },
    "corporate": { "label": "Corporate", "color": "#10B981" },
    "retail": { "label": "Retail", "color": "#A78BFA" }
  },
  "nodes": [
    {
      "id": "fed",
      "type": "gov",
      "label": "Federal Reserve",
      "subtype": "central_bank",
      "description": "US central bank — monetary policy, QE, reserve management",
      "metrics": {
        "total_assets_b": 7800,
        "inflow_velocity": "moderate",
        "outflow_velocity": "moderate",
        "confidence_pct": 90
      },
      "sources": [
        { "type": "treasury_issuance", "amount_b": 1200, "description": "Treasury bond proceeds deposited at Fed" }
      ],
      "destinations": [
        { "type": "qe_asset_purchases", "amount_b": 950, "target_node_types": ["gov", "corporate"], "description": "MBS and Treasury purchases" },
        { "type": "reserve_balances", "amount_b": 3200, "target_node_types": ["institutional"], "description": "Bank reserve balances at Fed" },
        { "type": "repo_operations", "amount_b": 150, "target_node_types": ["institutional"], "description": "Overnight and term repo" }
      ],
      "data_sources": ["Fed H.4.1", "FOMC Minutes", "New York Fed SRMA"]
    }
  ],
  "edges": [
    {
      "id": "edge_fed_to_banks",
      "source": "fed",
      "target": "jpmorgan",
      "amount_b": 450,
      "flow_type": "reserves",
      "direction": "outflow",
      "confidence_pct": 92,
      "data_sources": ["Fed H.8 (Commercial Banks)"]
    }
  ],
  "metadata": {
    "total_flow_tracked_b": 120500,
    "total_edges": 48,
    "total_nodes": 24,
    "active_flows": 31,
    "barometer_score": 58,
    "barometer_label": "Elevated"
  }
}
```

### Schema Details

#### `nodes[]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique node identifier (kebab-case) |
| `type` | enum | One of: `gov`, `institutional`, `crypto`, `corporate`, `retail` |
| `label` | string | Display name |
| `subtype` | string | Sub-category (e.g., `central_bank`, `hedge_fund`) |
| `description` | string | 1-sentence description |
| `metrics.total_assets_b` | number | Total assets under management / tracked ($B) |
| `metrics.inflow_velocity` | enum | `slow`, `moderate`, `fast`, `surge` |
| `metrics.outflow_velocity` | enum | `slow`, `moderate`, `fast`, `surge` |
| `metrics.confidence_pct` | number | Data confidence 0–100 |
| `sources[]` | array | Known capital sources (what feeds this node) |
| `sources[].type` | string | Source category |
| `sources[].amount_b` | number | Amount tracked ($B) |
| `sources[].description` | string | Human-readable explanation |
| `destinations[]` | array | Known capital destinations (where this node sends) |
| `destinations[].type` | string | Destination category |
| `destinations[].amount_b` | number | Amount tracked ($B) |
| `destinations[].target_node_types[]` | array | Which node types receive this |
| `destinations[].description` | string | Human-readable explanation |
| `data_sources[]` | array | Source URLs/docs for this node's data |

#### `edges[]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique edge identifier |
| `source` | string | Source node ID |
| `target` | string | Destination node ID |
| `amount_b` | number | Flow amount ($B) |
| `flow_type` | string | Category (e.g., `reserves`, `dividend`, `buyback`) |
| `direction` | enum | `inflow` (source→target expected), `outflow` (source→target is capital leaving the system) |
| `confidence_pct` | number | Data confidence 0–100 |
| `data_sources[]` | array | Source URLs/docs |

## 6. Visual Design Specification

### 6.1 Design Principles

1. **Frameless** — No shadows, no borders, no border-radius. Only 1px dividers.
2. **Dark command center** — Matching Event Horizon page (`#0F172A` background).
3. **Node-shape-by-type** — Each of the 5 types gets a distinct geometric shape.
4. **Edge-direction-by-color** — Inflows: green (`#10B981`), Outflows: red (`#EF4444`).
5. **Proportional sizing** — Node size scales with `total_assets_b`.
6. **Hover drill-down** — Hovering a node shows its sources/destinations in an overlay.
7. **No third-party libraries** — Pure CSS, HTML, SVG. No D3.js, no Chart.js.

### 6.2 Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--cn-bg` | `#0F172A` | Page background |
| `--cn-card` | `#1E293B` | Node background |
| `--cn-text` | `#E2E8F0` | Primary text |
| `--cn-muted` | `#94A3B8` | Secondary text |
| `--cn-dim` | `#64748B` | Tertiary / label text |
| `--cn-divider` | `rgba(255,255,255,0.08)` | 1px dividing lines |
| `--cn-gold` | `#D4AF37` | Governmental type |
| `--cn-blue` | `#3B82F6` | Institutional type |
| `--cn-amber` | `#F59E0B` | Crypto type |
| `--cn-green` | `#10B981` | Corporate type |
| `--cn-violet` | `#A78BFA` | Retail type |
| `--cn-red` | `#EF4444` | Outflows / negative |
| `--cn-green-plus` | `#10B981` | Inflows / positive |

### 6.3 Node Shapes (SVG)

```
GOVERNMENTAL      PRIVATE/INST       CRYPTO             CORPORATE          RETAIL
┌─────────┐       ◇─────────◇       ⬡───────⬡        ╭─────────╮       ╭─────╮
│  label  │       │  label  │       │ label  │        │  label  │       │label│
│  $ X.XB │       │  $ X.XB │       │ $ X.XB │        │  $ X.XB │       │$X.XB│
│ sources │       │ sources │       │ sources │        │ sources │       │ src │
│ dests   │       │ dests   │       │ dests   │        │ dests   │       │ dst │
└─────────┘       ◇─────────◇       ⬡───────⬡        ╰─────────╯       ╰─────╯

Rectangle         Diamond           Hexagon           Rounded-square    Circle
(building)        (portfolio)       (blockchain)      (corp. HQ)        (person)
```

### 6.4 Edge Rendering (SVG Paths)

Edges are SVG `<path>` elements with:
- **`stroke`**: green (`#10B981`) for inflow edges, red (`#EF4444`) for outflow
- **`stroke-width`**: proportional to `amount_b` (min 1px, max 8px, scaled linearly)
- **`stroke-dasharray`**: optional for low-confidence (<60%) edges
- **`marker-end`**: arrowhead matching stroke color
- **Opacity**: `0.6` default, `1.0` on hover

Edges route around nodes using quadratic Bézier curves (`Q` commands) to avoid
overlapping node bodies.

### 6.5 Layout Algorithm

A **static force-directed layout** computed at data-load time:

1. Place node types in columns (left-to-right): Gov → Institutional → Corporate → Retail → Crypto
   - This is a conceptual "capital flow direction": governmental policy → institutional
     intermediation → corporate investment → retail participation → crypto periphery
2. Within each column, sort nodes by `total_assets_b` descending
3. Vertically space nodes with padding proportional to number of edges
4. Route edges left-to-right with vertical offsets to prevent overlapping

### 6.6 Hover Interaction

When hovering a node:
- The node expands to show its source/destination detail panel
- All connected edges highlight (opacity 1.0, stroke-width +2px)
- All unconnected edges fade (opacity 0.15)
- A right-side info panel shows:
  - Node name, type, subtype
  - Total assets tracked ($B)
  - Source list with amounts
  - Destination list with amounts
  - Confidence score
  - Data source citations

### 6.7 Responsive Behavior

- **Desktop (>1024px)**: Full SVG graph with right-side info panel
- **Tablet (768-1024px)**: Graph shifts to vertical scroll; info panel becomes
  a bottom drawer triggered by tapping a node
- **Mobile (<768px)**: Nodes stack vertically in a list view; edges become
  indented connector lines; touch to expand node details inline

## 7. Implementation Plan

### 7.1 Files to Create

```
site/
  flow-nodes.html          ← Page entry point (HTML + inline CSS + JS)
  data/
    flow_nodes.json        ← Data file (node definitions, edges, metadata)
```

### 7.2 HTML Structure (`flow-nodes.html`)

```
<!DOCTYPE html>
<html>
<head>
  <style>
    /* ── CSS Variables ── */
    /* ── Page Layout ── */
    /* ── Node Styles (5 types) ── */
    /* ── Edge/Connector Styles ── */
    /* ── Info Panel Styles ── */
    /* ── Hover/Active States ── */
    /* ── Responsive ── */
  </style>
</head>
<body class="cn-body">
  <!-- Masthead (matching Event Horizon) -->
  <header class="cn-masthead">
    <div class="cn-masthead-left">
      <span class="cn-masthead-name">Capital Flow Nodes</span>
      <span class="cn-masthead-badge">Beta</span>
    </div>
    <div class="cn-masthead-right">
      <span id="cn-last-updated">—</span>
      <span id="cn-total-tracked">$—B tracked</span>
    </div>
  </header>

  <!-- Thesis -->
  <div class="cn-thesis">
    <h1>Capital Flow Nodes</h1>
    <p>Capital does not move randomly. It flows through structural conduits —
    governmental policy levers, institutional intermediation, corporate
    treasuries, retail participation, and crypto periphery. Each node is a
    source, a destination, or both. Hover any node to decompose its
    inflows and outflows.</p>
  </div>

  <!-- Node Graph (SVG) -->
  <div id="cn-graph-container">
    <svg id="cn-graph" viewBox="0 0 1200 800">
      <!-- Edges rendered as paths -->
      <!-- Nodes rendered as SVG groups -->
    </svg>
  </div>

  <!-- Info Panel (right sidebar) -->
  <aside id="cn-info-panel" class="cn-panel-hidden">
    <!-- Populated by JS on hover -->
  </aside>

  <!-- Legend -->
  <footer class="cn-legend">
    <div class="cn-legend-item" data-type="gov">Governmental</div>
    <div class="cn-legend-item" data-type="institutional">Institutional</div>
    <div class="cn-legend-item" data-type="crypto">Crypto</div>
    <div class="cn-legend-item" data-type="corporate">Corporate</div>
    <div class="cn-legend-item" data-type="retail">Retail</div>
  </footer>

  <script>
    // 1. Fetch flow_nodes.json
    // 2. Parse data
    // 3. Compute layout (column positions)
    // 4. Render SVG nodes and edges
    // 5. Attach hover handlers
    // 6. Animate on load
  </script>
</body>
</html>
```

### 7.3 JS Logic Flow

```
1. FETCH
   fetch('./data/flow_nodes.json') → parse JSON
   
2. COMPUTE LAYOUT
   type_order = ['gov', 'institutional', 'corporate', 'retail', 'crypto']
   column_x = { gov: 150, institutional: 350, corporate: 550, retail: 750, crypto: 950 }
   For each type:
     nodes_of_type = nodes.filter(n => n.type === type)
     sort by total_assets_b descending
     space vertically with (graphHeight / (count + 1)) spacing
   
3. BUILD NODE MAP
   node_map = { node.id → { ...node, x, y } }
   
4. RENDER EDGES (before nodes so nodes render on top)
   For each edge:
     src = node_map[edge.source]
     dst = node_map[edge.target]
     routePath = computeBezier(src, dst)
     <path d={routePath} class="cn-edge inflow|outflow" 
           style="stroke-width: scaledWidth" />
   
5. RENDER NODES
   For each node:
     <g class="cn-node" data-node-id={node.id}>
       <shape type={node.type} x={x} y={y} size={scaledSize} />
       <text>{node.label}</text>
       <text>${format(node.metrics.total_assets_b)}B</text>
     </g>
   
6. ATTACH INTERACTIONS
   nodeGroup.addEventListener('mouseenter', showNodeDetails)
   nodeGroup.addEventListener('mouseleave', hideNodeDetails)
   showNodeDetails: highlight edges, populate info panel
   hideNodeDetails: reset edge opacity, hide info panel
```

### 7.4 SVG Shape Definitions

Each shape is a `<path>` or `<g>` that renders at position (0,0) and is
translated to the computed position:

**Rectangle** (gov): `M -60,-30 L 60,-30 L 60,30 L -60,30 Z`

**Diamond** (institutional): `M 0,-40 L 50,0 L 0,40 L -50,0 Z`

**Hexagon** (crypto):
```
M 0,-35 L 30,-17.5 L 30,17.5 L 0,35 L -30,17.5 L -30,-17.5 Z
```

**Rounded-square** (corporate): 
```
M -50,-25 Q -50,-30 -44,-30 L 44,-30 Q 50,-30 50,-25 L 50,25 Q 50,30 44,30 L -44,30 Q -50,30 -50,25 Z
```

**Circle** (retail): `cx="0" cy="0" r="30"`

## 8. Edge Routing Algorithm

For edges between nodes in adjacent columns (left→right):

```
function computeBezier(src, dst) {
  const dx = dst.x - src.x;
  const dy = dst.y - src.y;
  const cp_offset = dx * 0.4;  // control point horizontal offset
  return `M ${src.x + nodeWidth/2},${src.y} 
          C ${src.x + cp_offset},${src.y} 
            ${dst.x - cp_offset},${dst.y} 
            ${dst.x - nodeWidth/2},${dst.y}`;
}
```

For edges that would overlap (parallel edges between same two nodes):
- Offset the control points vertically by `sin(index) * 15` pixels

## 9. Data Quality & Confidence System

Each node and edge carries a `confidence_pct` field (0-100):

| Range | Label | Visual Effect |
|-------|-------|---------------|
| 90-100 | Very High | Solid stroke, full opacity |
| 70-89 | High | Solid stroke, 0.8 opacity |
| 50-69 | Medium | Dashed stroke (`stroke-dasharray: 6,4`) |
| 30-49 | Low | Dotted stroke (`stroke-dasharray: 2,4`) |
| 0-29 | Speculative | Dotted stroke, 0.4 opacity, italic label |

## 10. Future Enhancements (Post-MVP)

1. **Flow animation** — SVG `<animate>` particles moving along edges
2. **Time scrubber** — View node states at different timestamps
3. **Node search/filter** — Filter by type, subtype, amount threshold
4. **Expandable nodes** — Click a node to see its sub-types as children
5. **Comparison mode** — Side-by-side view of two timestamps
6. **Sankey overlay** — Toggle between node-link and sankey layout
7. **Z.1 matrix tab** — Raw sector-by-sector matrix view
8. **Edge bundling** — Hierarchical edge bundling for crowded graphs

---

*Specification v1.0 — Gazzetta di Kyiv Capital Flow Nodes*
*Research sources: Fed Z.1 Release Guide, Bloomberg CRPH Function,
Refinitiv Eikon Flow of Funds, EPFR Global, SEC 13F filings,
Glassnode Exchange Flow Report, BIS International Banking Statistics*
