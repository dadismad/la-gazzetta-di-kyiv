# Focus Group Pipeline Specification

**Gazzetta di Kyiv — Multi-Industry Focus Group Architecture**
**Version:** 3.0.0
**Status:** APPROVED
**Date:** June 2026

---

## 1. RATIONALE

Gazzetta di Kyiv is a contradiction-first financial intelligence site. Every story, flow, and signal must be stress-tested from **every relevant professional vantage point**. A focus group limited to finance and design personas creates blind spots — a grain trader sees different capital flow implications than a defense contractor analyst, and both see different things than a retail investor or a sanctions lawyer.

This pipeline expands from ~20 finance/design/journalism personas to **35+ personas across 14 industries**, each with **four evaluation lenses** (top-down, bottom-up, sourced analysis, competitive threat) and a **5-phase pipeline** with weighted evaluation methodology.

### 1.1 Design Principles

| Principle | Implication |
|-----------|-------------|
| **Contradiction-first** | Personas are selected to MAXIMIZE disagreement — groupthink is the enemy. Every batch mixes industries, seniority, and stake |
| **Capital-first lens** | Every persona, regardless of industry, must answer: "Where is the money going?" from their vantage point |
| **Actionable output** | Every persona must produce a specific trade/action/decision, not just criticism |
| **Freshness gate** | No stale data survives — every review starts with data freshness verification |
| **Weighted evaluation** | Top-down (40%) + Bottom-up (60%) combined score determines PASS/CONDITIONAL/FAIL |

---

## 2. INDUSTRY COVERAGE — 35+ PERSONAS ACROSS 14 INDUSTRIES

### 2.1 Finance & Investment (Existing — 5 personas, enhanced with new lenses)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 1 | **Portfolio Manager (Top-Down Macro)** | Does the site's macro narrative align with my book's thesis? What systemic risk does the data reveal? | Is the net exposure signal clear? Can I extract a single allocation action in ≤30s? | Bloomberg Terminal, Goldman research, IMF data | The speed at which flows are surfaced vs. consensus — a 2h lead on institutional flow direction is $2M edge |
| 2 | **Retail Degen Trader** | Does the site make me feel like I have an edge the market doesn't? What's the narrative I can ape into? | Is the trade idea clear? Ticker + direction + entry trigger — if I can't copy-trade in 10 seconds it's dead | Twitter/X, Discord groups, Crypto Twitter influencers | Crowd psychology — if retail is positioned one way and institutions another, the contrarian signal is the real edge |
| 3 | **55-Year-Old Retail Investor** | Is this site trying to sell me something, or give me an honest edge? What would make me trust it with real capital? | Can I understand the portfolio implication in 10 seconds? Are labels clear without finance jargon? | Morningstar, WSJ, Bloomberg TV | Behavioral — older retail holds through drawdowns; the signal is whether the site acknowledges their risk tolerance |
| 4 | **Hedge Fund Quant** | What's the alpha decay curve? How quickly does the site's signal become consensus and lose its edge? | Are the data formats parseable? Can I backtest the signal? What's the Sharpe ratio of following the site's plays? | Bloomberg, custom backtesting infrastructure, alternative data feeds | The gap between narrative signal and price signal — which stories anticipate price moves vs. react to them |
| 5 | **Private Equity / VC Principal** | What structural dislocations does the site reveal? Which sectors are under-allocated capital? Where's the next wave? | Is the deal flow data actionable? What companies/verticals should I be diligence-ing that aren't on my radar? | PitchBook, Crunchbase, proprietary LP networks | Capital formation signals — following where VCs deploy vs. where they say they deploy |
| 6 | **Derivatives / Options Market Maker** | Does the site surface volatility regime shifts before the options market reprices? | Are there specific strike/expiry combos implied by the flow data? What's the vega exposure? | Options clearing data, futures open interest, gamma exposure reports | The delta between spot narrative and derivatives positioning — 90% of retail watches spot, but the smartest money is in vol |

### 2.2 Energy (NEW — 4 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 7 | **Oil & Gas Trader** | What's the macro flow direction in crude? Does the site's geopolitical narrative align with physical crude flows? | Is there a specific crude grade/basis play? WTI vs. Brent spread? Contango/backwardation signal? | Vortexa, Kpler, S&P Global Platts, ICE data | Physical flow leads paper — tanker tracking data reveals positioning 2-3 weeks before EIA reports |
| 8 | **Renewables / Clean Energy Analyst** | Does the site track the capital rotation from fossil to renewable infrastructure? Is the IRA/Inflation Reduction Act impact modeled? | What specific renewable assets or companies are positioned for capital inflow? Solar vs. wind vs. battery storage allocation? | BNEF, IRENA, EIA, project finance databases | Subsidy arbitrage — which markets are due for policy-driven repricing that consensus hasn't priced in |
| 9 | **Grid Operations / Power Markets Expert** | What does the site's macro picture imply for electricity demand? Is the AI/DC buildout adequately reflected in power price forecasts? | Is there a specific power market (PJM, ERCOT, CAISO) with a pricing dislocation? What's the heat-rate signal? | ISO/RTO data, S&P Global, Platts Megawatt Daily | The load growth surprise — AI data centers and reshoring create power demand that ISO forecasts systematically underestimate |
| 10 | **Energy Policy / Geopolitical Risk Analyst** | Does the site's story architecture capture the energy-security nexus? Are pipeline politics, sanctions, and OPEC+ dynamics properly weighted? | What specific energy policy catalyst (EU ETS reform, US LNG export pause, OPEC+ quota change) is mispriced by markets? | IEA, OPEC MOMR, EIA STEO, EU energy policy tracker | The gap between political rhetoric and physical infrastructure reality — pipelines take 5+ years, but policy changes in months |

### 2.3 Defense & Aerospace (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 11 | **Defense Contractor / Industry Analyst** | Does the site track the global defense spending supercycle? Are NATO burden-sharing, EU defense fund, and US supplemental tracked as capital flow drivers? | What specific prime contractor (Lockheed, RTX, Rheinmetall, Leonardo) or subsystem supplier benefits from identified conflicts? | Janes, Defense News, SIPRI, DoD budget docs, SEC filings | The gap between defense budget authorization and actual procurement — contract awards lag budgets by 12-24 months |
| 12 | **Military Logistics / Operations Analyst** | What does the site's geopolitical narrative imply for deployed force posture, supply chain resilience, and contested logistics? | Is there a specific theater (Ukraine, Taiwan strait, Middle East) where logistics data reveals preparation for escalation or de-escalation? | OSINT sources, satellite imagery analysis, defense attaché reports | Ammunition burn rates and replacement timelines — stockpile data is the best leading indicator of operational tempo |
| 13 | **Arms Trade / Defense Procurement Researcher** | Does the site track the second-order effects of arms transfers? Who's arming whom and what does it mean for regional power balances? | What specific defense export deal or offset agreement is under-reported and has equity implications? | SIPRI Arms Transfers Database, export license approvals (DDTC, BAFA), trade press | The shadow arms trade — drone tech transfer from Iran to Russia, Chinese components in Western systems — flows that official databases miss for 3-5 years |

### 2.4 Agriculture & Commodities (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 14 | **Grain / Soft Commodities Trader** | What does the site's macro and weather narrative imply for global crop supply? Are Black Sea, La Niña, and export policy risks modeled? | Is there a specific basis play (Kansas City v. Chicago wheat)? What's the implied carry? Are there protein-to-grain spread trades? | USDA WASDE, MDA weather, Refinitiv Agriculture, CME data | The 2-week weather forecast vs. the 6-month soil moisture trend — consensus trades the weather, but the money is in subsoil moisture trends that take months to reverse |
| 15 | **Softs / Beverage & Fiber Analyst** | What structural demand shift (decarbonization, China slowdown, reshoring) impacts soft commodity demand curves? | Is there a specific soft commodity (palm oil, sugar, cocoa, cotton, coffee) with a weather/policy supply shock that futures haven't priced? | ICE data, USDA FAS, International Coffee Organization, ISO sugar data | The consumption-inventory delta — soft commodity stock-to-use ratios that official forecasts miss because demand growth exceeds GDP modeling assumptions |
| 16 | **AgTech / Agricultural Supply Chain Analyst** | Does the site capture the capital flows into vertical farming, precision ag, and alternative proteins? What's the real vs. hype ratio? | What specific agtech companies or technologies have real deployment data vs. fundraising narratives? | AgFunder, PitchBook, USDA research, company disclosures | The deployment gap — pilot project to commercial scale is the hardest transition in agtech, and most analysts miss the failure rate at this stage |

### 2.5 Shipping & Logistics (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 17 | **Maritime Insurance / P&I Underwriter** | Does the site track war risk premiums, sanctions enforcement, and rerouting in maritime corridors? What's the systemic risk in Red Sea, Black Sea, Taiwan strait? | Is there a specific vessel class or flag state with changing risk profile? What's the war risk premium trajectory for the Bab el-Mandeb or Malacca strait? | London insurance market, Clarksons, Baltic Exchange, IMO data | The correlation between P&I club claims data and trade route shifts — insurance data leads official trade statistics by 4-6 weeks |
| 18 | **Freight Forwarder / Logistics Operator** | What does the macro picture imply for container freight rates, bulk shipping demand, and supply chain reconfiguration? | Is there a specific trade lane (Asia-Europe, Trans-Pacific) with capacity dislocation or rate inflection that affects goods pricing? | Freightos Baltic Index (FBX), Drewry, Xeneta, SCFI | The difference between published spot rates and actual pocket rates (loyalty discounts, volume commitments) — published rates are 20-30% above what large shippers actually pay |
| 19 | **Port Operations / Maritime Infrastructure Analyst** | Does the site track port congestion, infrastructure investment, and strategic port acquisitions (Belt and Road, nearshoring)? | What specific port (Rotterdam, Shanghai, LA/LB, Santos) has a congestion or investment signal that affects regional trade flow? | Port authority data, IHS Markit, Lloyd's List, satellite port monitoring | The real-time vs. reported congestion gap — port queues and anchorage data from AIS satellite feeds show congestion 2-3 weeks before official port authority reports |

### 2.6 Telecommunications & Infrastructure (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 20 | **5G / Spectrum Policy Analyst** | Does the site track the global spectrum allocation race? What does 6G R&D expenditure tell us about the next technology cycle? | Is there a specific spectrum band (C-band, mmWave, mid-band) or regional allocation (Europe 6G, US DoD mid-band sharing) with mispriced implications? | Ofcom, FCC, ITU, GSMA, company R&D disclosures | The patent-to-product gap — standard-essential patent filings in 6G reveal R&D direction 3-5 years before commercial deployment |
| 21 | **Data Center / Cloud Infrastructure Analyst** | Does the site capture the AI-driven data center buildout? What does power/water constraints imply for data center geography? | What specific data center market (Northern Virginia, Frankfurt, Singapore, Jakarta) faces power or water constraints that will constrain supply? | datacenterHawk, JLL Data Center Reports, hyperscaler capex disclosures | The power procurement lead time — data center operators secure power interconnection agreements 3-5 years before opening, making these permits the best leading indicator |
| 22 | **Telecom Network Engineer / Infrastructure Operator** | What structural shifts in network architecture (Open RAN, fiber-to-the-home, satellite broadband) create capital allocation opportunities? | Is there a specific operator or market where a network upgrade cycle (5G SA, fiber deep, cable DOCSIS 4.0) creates a capex inflection? | Ookla, Opensignal, Dell'Oro Group, company capital plans | The actual vs. declared coverage gap — operator coverage maps are marketing; real user speed test data from Ookla reveals actual network quality |

### 2.7 Pharmaceuticals & Biotech (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 23 | **Drug Development / Clinical Trials Analyst** | Does the site track the regulatory risk landscape for pharma? What FDA, EMA, or NMPA policy shifts affect the pipeline? | Is there a specific trial phase transition or drug approval decision that creates asymmetric upside not priced in? | ClinicalTrials.gov, FDA calendar, company pipeline disclosures, EvaluatePharma | The data-readout-to-publication gap — Phase 2/3 top-line results known to regulators and sponsors 2-4 weeks before public disclosure |
| 24 | **Healthcare Policy / Market Access Analyst** | What macro trends (aging population, GLP-1 expansion, biosimilar adoption, IRA price negotiation) reshape pharma profitability? | What specific drug pricing policy (IRA Medicare negotiation, EU HTA harmonization, Japan NHI repricing) creates a catalyst event? | IQVIA, SSR Health, Kaiser Family Foundation, EC HTA regulations | The formulary access gap — which drugs get preferred PBM/insurance formulary placement (revealed by off-invoice rebates) often differs from public coverage decisions for 6-12 months |
| 25 | **Biotech Patent / IP Strategist** | Does the site capture the innovation concentration risk? Are breakthrough patents concentrated in a few firms, creating systemic risk? | What specific patent cliff (Keytruda 2028, Humira already, Stelara 2025) creates an opportunity for biosimilar entrants that markets haven't modeled? | USPTO, WIPO, patent landscape analyses, FDA Orange Book | The patent challenge pipeline — Paragraph IV filings (ANDA challenges) are filed years in advance but only surface publicly when the lawsuit is filed, giving early movers a 12-18 month preparation window |

### 2.8 Cybersecurity & Intelligence (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 26 | **Threat Intelligence Analyst** | Does the site's geopolitical narrative align with observed state-sponsored cyber operations? Are digital conflict dynamics (kinetic vs. cyber thresholds) tracked? | What specific sector (energy grid, financial system, telecom backbone) shows elevated adversary reconnaissance that precedes attack? | Mandiant, CrowdStrike, Recorded Future, CISA alerts, VX Underground | The dwell time gap — adversaries are present in networks for an average of 10 days before detection; intelligence reports lag by 2-4 weeks, creating a critical window for proactive defense |
| 27 | **APT Researcher / State-Sponsored Operations Analyst** | Does the site track the national security implications of cyber operations? What's the relationship between cyber ops and conventional military posture? | Is there a specific APT group (APT10, APT29, Kimsuky, Lazarus) changing TTPs or targeting sectors that reveals strategic intent? | Telegram (threat actor channels), VirusTotal, MalwareBazaar, industry incident reports | The tool-sharing overlap — when two APT groups share C2 infrastructure or malware code (e.g., China-linked APT10 using North Korea-linked Lazarus tooling), it signals operational collaboration that attribution teams miss for 6-12 months |
| 28 | **Zero-Day Broker / Vulnerabilities Markets Analyst** | Does the site capture the shadow economy dynamics of the exploit market? What does pricing of zero-days tell us about defensive weakness? | What specific software/OS vulnerability class (iOS kernel, Windows CLFS, Chrome renderer) has zero-day market pricing that signals a defensive gap? | Exploit broker price lists (Zerodium, Crowdfense), CVE databases, Project Zero disclosures | The exploit-to-patch cycle gap — brokers sell zero-days to governments that are used for 6-12 months before public disclosure, creating an "exploited but not disclosed" category of risk invisible to the market |

### 2.9 Real Estate & Property (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 29 | **Commercial REIT Analyst** | Does the site track the capital migration across real estate sectors? Office-to-residential conversions? Industrial absorption from nearshoring? | What specific REIT (office, industrial, multifamily, self-storage, data center, healthcare) has a NAV/share discount or sector rotation catalyst? | NAREIT, Green Street Advisors, RCA, CoStar | The appraisal-to-market gap — REIT NAVs are based on appraisals that lag market transactions by 6-12 months; the best leading indicator is cap rate compression in private transaction data |
| 30 | **Cross-Border Property Flows Analyst** | Does the site track global capital flows into real estate? Which jurisdictions are receiving sovereign wealth and billionaire capital flight? | What specific city/neighborhood (Miami, Dubai, Singapore, Sao Paulo) shows abnormal luxury purchase volume that signals capital flight from a specific region? | Knight Frank, JLL, Savills, wealth reporting, property registry data | The beneficial ownership gap — opaque ownership structures (trusts, offshore companies) hide 30-50% of cross-border luxury transactions; notarial and corporate registry data reveals patterns 12-24 months delayed |
| 31 | **Property Insurance / Catastrophe Risk Analyst** | Does the site capture the systemic risk from climate change on real estate values? What markets face uninsurability inflection points? | What specific metro area (Miami Beach, Houston, Paradise CA) or property type (Florida coastal, California wildfire zone) faces insurance premium spikes that create a value-at-risk repricing? | NOAA, FEMA NFIP data, state insurance department filings, RMS/AIR catastrophe models | The insurance non-renewal map — insurers' internal non-renewal decisions for specific ZIP codes lead public rate filings by 12-18 months, revealing future uninsurability zones before the market prices the risk |

### 2.10 Luxury & Art Market (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 32 | **Art Advisor / Fine Art Market Strategist** | Does the site capture art as an alternative asset class? What macro trends (generational wealth transfer, wealth destruction, repatriation) affect art pricing? | What specific artist segment (Blue Chip old masters, Post-War & Contemporary, Ultra-Contemporary, Latin American) has a pricing dislocation vs. auction results? | Artnet, Sotheby's/Christie's databases, Artprice, ArtTactic confidence surveys | The private-sale-to-auction gap — 60%+ of high-value art transactions happen privately and are not published; the whispers in advisory networks (new museum endowments, sovereign wealth art buying) lead auction visibility by 6-18 months |
| 33 | **Auction House Specialist / Collectibles Expert** | Does the site track capital flows into alternative collectibles (watches, handbags, wine, classic cars, rare spirits, trading cards)? | What specific collectible category shows a price dislocation from the equity cycle? Are luxury goods serving as a leading or lagging indicator of wealth? | Chrono24 (watches), Knight Frank Luxury Index, Liv-ex (wine), HAGI (classic cars) | The hyper-luxury volume-to-price relationship — in a downturn, the top 1% of lots by price hold value while the bottom 99% correct, a divergence visible in real-time auction data but not in quarterly indices |
| 34 | **Cultural Heritage / Provenance Researcher** | Does the site track repatriation claims and their impact on museum collections and the art trade? What legal / regulatory shifts affect cultural property movement? | What specific repatriation claim (Benin Bronzes, Parthenon Marbles, Pazyryk collection) creates a regulatory precedent that affects all museum deaccessioning? | UNESCO 1970 Convention tracker, museum repatriation statements, ICOM red lists, ILAB | The provenance research gap — most museums have published only 30-50% of their digitized provenance records; the remaining records contain repatriation risk that surfaces only during sale, creating insurance and title liability |

### 2.11 Legal & Regulatory (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 35 | **Sanctions / OFAC Compliance Lawyer** | Does the site capture the systemic risk of secondary sanctions? What's the trajectory of sanctions enforcement (Iran, Russia, Venezuela, North Korea) and its impact on trade finance? | What specific jurisdiction (UAE, Turkey, Kazakhstan) or sector (shipping, crypto, gold trading) faces elevated OFAC enforcement that creates operational risk? | OFAC SDN list, EU sanctions tracker, UK OFSI, court filings, discussion with peer firms | The guidance-to-enforcement gap — OFAC issues general guidance 6-18 months before bringing enforcement actions; knowing which industry the next enforcement wave targets creates a first-mover exit advantage |
| 36 | **Trade Compliance / Customs Specialist** | Does the site track the structural reshaping of global trade (tariffs, export controls, CHIPS Act, supply chain decoupling)? What's the real vs. reported trade flow data? | Is there a specific tariff line or export control classification (ECCN) that creates a pricing dislocation or supply chain choke point? | US Customs data, BIS entity list, EU dual-use regulation, WTO dispute tracker | The customs valuation gap — importers systematically under-invoice (trade misinvoicing) by 20-50% on certain product categories; mirror trade statistics (export vs. import data from trade partners) reveal real capital flows |
| 37 | **CFIUS / FDI Screener** | Does the site track cross-border M&A and greenfield investment screening? What sectors face heightened CFIUS, FIRRMA, and EU FDI screening? | What specific technology sector (quantum, semiconductor, AI, biotech) or target company faces a CFIUS or FIRRMA review that creates a deal risk or break-up fee arbitrage? | CFIUS annual report, FIRRMA filings, EU FDI screening register, GPI | The pre-filing notification gap — companies must notify CFIUS 30-45 days before a filing; deal-side advisors know when a CFIUS block is coming and position accordingly 6-8 weeks before public news |

### 2.12 Academia & Research (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 38 | **Political Scientist (International Relations)** | Does the site's narrative structure capture the correct levels of analysis? Are stories framed at the systemic level (polarity, balance of power), state level (regime type, foreign policy), or individual level (leader psychology)? | What specific IR theory (offensive realism, liberal institutionalism, constructivism) would predict a different outcome than the site's stated trade idea? | Academic journals (IO, APSR, EJIR), think tanks (CSIS, Chatham House, SWP), primary source documents | The academic-to-policy translation gap — academic IR research has 3-5 year lead time before it reaches policy circles; the best unhedged geopolitical predictors are PhD theses and faculty working papers |
| 39 | **Econometrician / Applied Economist** | Does the site's capital flow tracking use the correct statistical models for regime detection? Are the macro indicators properly lagged, filtered, and detrended? | What specific econometric model (VAR, regime-switching, synthetic control) would identify a different regime change signal than the site's current methodology? | NBER, BIS working papers, Fed research, academic replication databases | The model specification advantage — the choice of lag structure, detrending method, and variable selection in macro models produces different regime signals; proprietary specs that beat standard models (e.g., AIC-optimized VARs) are the true edge |
| 40 | **Game Theorist / Strategic Decision Theorist** | Does the site's narrative modeling incorporate strategic interaction? Are actors modeled as rational agents with aligned/disaligned preferences? | What specific game (prisoner's dilemma, chicken game, coordination game, zero-sum) best describes each identified geopolitical conflict? What are the Nash equilibria? | Formal modeling papers, experimental economics results, historical case studies re-analyzed through game theory | The payoff matrix gap — most geopolitical analysis assumes fixed preferences, but game theorists know payoffs change as the game is iterated; identifying when the payoff structure is about to shift (e.g., elections, economic crisis) creates a 2-3 move prediction advantage |

### 2.13 Retail & Consumer (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 41 | **Consumer Sentiment / Behavior Analyst** | Does the site capture the divergence between consumer sentiment (soft data) and consumer spending (hard data)? What's the real income/consumption trajectory? | What specific consumption category (durables, services, experiences, staples) shows a divergence from the macro narrative that signals a regime shift? | University of Michigan Consumer Survey, BLS CES, Redbook research, Plaid transaction data, JP Morgan Chase Institute | The transaction-to-survey gap — consumer sentiment surveys (Michigan, Conference Board) lag real transaction data by 4-8 weeks; aggregated anonymized credit/debit card transaction data reveals actual consumption changes before surveys do |
| 42 | **Supply Chain Retail Analyst / Demand Forecaster** | Does the site track the inventory cycles across retail? Are destocking/reordering cycles identified as leading indicators of manufacturing PMI? | What specific retail category (apparel, electronics, home goods, auto parts) shows an inventory-to-sales ratio dislocation that signals a pricing or production inflection? | Census Bureau wholesale/retail data, logistics providers, company 10-K MD&A, Blue Yonder demand signals | The sell-through vs. inventory gap — real-time point-of-sale data from retailers is the most accurate demand signal; consensus relies on store-shipment data which is 4-6 weeks delayed and confounds real demand with inventory positioning |
| 43 | **E-commerce / Marketplace Strategist** | Does the site capture the structural shift in commerce? Are marketplace take rates, ad revenue growth, and logistics-as-a-service trends tracked as capital flow indicators? | What specific marketplace (Amazon, Shopify, Temu, SHEIN, Mercado Libre, Sea Limited) shows a take rate or GMV inflection that signals a competitive regime change? | Marketplace Pulse, eCommerceDB, SimilarWeb, Sensor Tower, company disclosures | The marketplace data gap — Amazon and other platforms control a walled garden of transaction data; third-party sellers and aggregators (Thrasio, Perch, Boosted) have the best view of category-level demand shifts, 4-6 weeks before public reporting |

### 2.14 Mining & Metals (NEW — 3 personas)

| # | Persona | Top-Down Lens | Bottom-Up Lens | Source Trust | Info Asymmetry |
|---|---------|---------------|----------------|-------------|----------------|
| 44 | **Rare Earths / Critical Minerals Analyst** | Does the site capture the concentration risk in critical mineral supply chains? What's the China de-risking timeline and its impact on mineral prices? | What specific critical mineral (lithium, cobalt, nickel, graphite, rare earth oxides, gallium, germanium) faces a supply/demand imbalance that spot markets haven't priced? | USGS Mineral Commodity Summaries, EU Critical Raw Materials Act tracker, Benchmark Mineral Intelligence, SMM | The processing vs. mining gap — everyone tracks mine supply, but the bottleneck is processing; China controls 60-90% of processing capacity across most critical minerals, and expansion plans outside China face 5-7 year lead times |
| 45 | **Gold / Precious Metals Trader** | Does the site's macro architecture correctly model gold as a monetary metal vs. a commodity? Are central bank reserve dynamics, real rates, and currency debasement correctly weighted? | Is there a specific gold market dislocation (LBMA vs. COMEX, Shanghai premium, London-GOFO backwardation) that signals a physical market squeeze or regime shift? | LBMA, World Gold Council, COMEX data, central bank reserve disclosures (IMF COFER) | The physical gold flow gap — London-New York gold arbitrage reveals physical flow direction; when gold moves from London (bullion bank inventory) to New York/Shanghai (end-user markets), it signals structural demand exceeding paper market capacity |
| 46 | **Base Metals / Battery Metals Trader** | What does the site's macro picture imply for the commodity supercycle thesis? Are electrification, reshoring, and infrastructure spending adequately modeled as demand drivers? | Is there a specific base metal (copper, aluminum, zinc, nickel, tin) with a storage/contango structure that signals a physical market regime change? | LME, SHFE, COMEX, CRU Group, Wood Mackenzie, Fastmarkets | The warranting vs. actual stock gap — LME warehouses report warranted stocks, but physical metal transacted off-exchange (off-warrant, leased, finance stocks) can be 2-3x reported levels; the off-warrant stock trajectory is the real price signal |

---

## 3. EVALUATION METHODOLOGY

### 3.1 Top-Down Evaluation (Weight: 40%)

**Purpose:** Examine the site from a systemic lens — does the architecture hold? Are paradigms consistent? Does the capital-first lens hold?

**Dimensions (scored 1-10 each):**

| Dimension | Key Question | Scaling |
|-----------|-------------|---------|
| **Architecture Integrity** | Does the container structure (Stories → Flows → Anchor → Signal) form a logical chain, or are containers adjacent but unconnected? | 10 = perfect deductive chain; 1 = random panels |
| **Paradigm Consistency** | Are the six paradigm pillars consistently tracked across stories, flows, and signals? Do stories map to pillars correctly? | 10 = every story cites a pillar with evidence; 1 = stories contradict their assigned pillar |
| **Capital-First Lens** | Does every element answer "where is the money going?" Or are there decorative/vanity metrics? | 10 = every visible stat is tradeable; 1 = hero with no action implication |
| **Contradiction Resolution** | Are contradictions surfaced and resolved, or hidden? Are They Say/Reality pairs sharp? | 10 = every reality claim is falsifiable and sourced; 1 = straw-man constructions |
| **Comprehensibility Ceiling** | Can a non-finance professional understand the architecture in 30 seconds? | 10 = labels are concrete and benefit-focused; 1 = jargon and internal terminology |

**Top-Down Score = (Sum of 5 dimensions) / 5**

### 3.2 Bottom-Up Evaluation (Weight: 60%)

**Purpose:** Examine every element individually — is this label clear? Is this number actionable? Does this card render correctly?

**Dimensions (scored 1-10 each):**

| Dimension | Key Question | Scaling |
|-----------|-------------|---------|
| **Label Clarity** | Does every visible label tell you what it measures in ≤2 words? | 10 = concrete prefix + metric (Flow confidence); 1 = ambiguous abstract (Confidence) |
| **Number Actionability** | Can every number be traded/acted upon? Does it carry direction, magnitude, and unit? | 10 = number includes direction (↑↓), delta (%), asset class; 1 = number with no context |
| **Card Rendering** | Do all containers render without layout breaks, truncation, or missing data? | 10 = pixel-perfect; 1 = broken layout |
| **Data Freshness** | Is every stat current within the defined freshness window? | 10 = all data <2h old; 1 = stale data displayed |
| **Cross-Container Consistency** | Do labels and metrics mean the same thing across all containers? | 10 = taxonomy is consistent; 1 = "confidence" means different things in different places |
| **Mobile Readability** | Is every element legible and tappable at 390px viewport? | 10 = flawless mobile experience; 1 = unreadable |
| **Source Attribution** | Can the reader find the source for every data point? | 10 = every number links to its source; 1 = numbers appear from nowhere |
| **Accessibility (alt text, ARIA, contrast)** | Are non-visual users accommodated? | 10 = WCAG AA compliant; 1 = no alt text |
| **Internationalization** | Are all user-facing strings in the i18n system? Any hardcoded English? | 10 = 100% i18n; 1 = mixed hardcoded/translated |
| **Error Resilience** | What happens when data is missing, malformed, or delayed? | 10 = graceful loading/error states everywhere; 1 = blank containers |

**Bottom-Up Score = (Sum of 10 dimensions) / 10**

### 3.3 Combined Scoring (The Verdict)

| Combined Score | Verdict | Action |
|---------------|---------|--------|
| **≥ 8.0** | PASS | None — proceed to continuous improvement phase |
| **6.0 – 7.99** | CONDITIONAL PASS | Fix identified issues before next cycle; re-review in maintenance phase |
| **< 6.0** | FAIL | Block next editorial cycle; fix critical issues before any forward progress |

**Combined Score = (Top-Down × 0.40) + (Bottom-Up × 0.60)**

### 3.4 Per-Persona Scoring Template

```
## Persona: [Name] — [Industry]
**Score:** [Top-Down X/10 | Bottom-Up Y/10 | Combined Z/10]
**Biggest Praise:** [1-sentence]
**Biggest Complaint:** [1-sentence]

### Top-Down Findings
- [Systemic issue or affirmation]

### Bottom-Up Findings
- [Specific element with location]

### Sourced Analysis
- Where I'd verify: [source list]
- Trust score for this site's data: [1-10]
- What source would make me trust it more: [specific]

### Competitive Threat Score: [1-10]
- What information asymmetry does this create?
- Who loses and who wins if this data is real?
- What trade can I execute right now based on this?
```

---

## 4. 5-PHASE PIPELINE ARCHITECTURE

### Phase 1: PRE-REVIEW — Data Freshness & Readiness

**Goal:** Ensure the review target is fresh, accurate, and loaded with current data before any persona evaluates it.

**Sub-steps:**

1. **Data freshness check**
   - Check `stories.json` mtime → must be < 2h old
   - Check `flows.json` mtime → must be < 2h old
   - Check `index.html` deployed timestamp (GCS object metadata)
   - If any stale > 2h: trigger data pipeline before proceeding

2. **Source attribution check**
   - Verify every story in `stories.json` has a `source_url` and `source_name`
   - Verify every flow in `flows.json` has a source description
   - Log any missing attribution as pre-review warnings

3. **Live site verification**
   ```bash
   curl -sI "https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html" | grep -q "200"
   ```
   - If 404: CANNOT ASSESS visual metrics; content-only review
   - If 200: verify CDN has fresh content (not cached stale version)
     - `gsutil cp gs://www.lagazzettadikyiv.com/index.html - | grep '<new-element-or-date-marker>'`

4. **Persona selection**
   - Select 10 personas max (5 per batch)
   - Mix: 2-3 finance, 2-3 industry-specific, 1-2 generalist, 1-2 contrarian
   - Record selection rationale in the batch config

**Output:** `pre-review-report.md` with freshness stamps, attribution stats, site health status, and persona selection.

### Phase 2: REVIEW — Multi-Persona Focus Group (2 Batches)

**Goal:** Spawn personas in two sequential batches (5 each) to avoid overwhelming context windows and allow first batch's findings to inform second batch focus.

#### Batch 1: Initial Scan (5 personas)
- **Mix:** 2 finance/industry core + 2 specific-industry + 1 contrarian/generalist
- **Execution:** All 5 spawn in parallel via `delegate_task(browser)`
- **Focus:** High-level architecture, data integrity, first impressions, contradictions
- **Prompt structure for each persona:**
  ```
  You are [PERSONA]. Visit {URL}.
  
  Evaluate through FOUR lenses:
  1. **TOP-DOWN ([X] view)** — [tailored systemic question]
  2. **BOTTOM-UP ([Y] view)** — [tailored specific question]
  3. **SOURCE TRUST** — Where would I verify this data? What sources do I trust/lack?
  4. **COMPETITIVE THREAT** — What information asymmetry does this create?
  
  Score each lens 1-10.
  Biggest praise (one sentence).
  Biggest complaint (one sentence).
  ```

#### Batch 2: Targeted Investigation (5 personas)
- **Mix:** 2 fresh industry perspectives + 1 technical/deep-dive + 1 user experience + 1 Machiavellian/Aesthetic
- **Execution:** Run AFTER Batch 1 output is collected
- **Focus:** Deep-dive on issues identified in Batch 1, plus blind-spot coverage
- **Contradiction injection:** If Batch 1 showed strong consensus, Batch 2 selects contrarian personas deliberately designed to disagree

**Output:** `batch-1-report.md` and `batch-2-report.md` with per-persona structured feedback.

### Phase 3: POST-REVIEW — Aggregate & Prioritize

**Goal:** Combine all 10 persona outputs into a single structured report with priority ordering.

**Sub-steps:**

1. **Consensus Catalog** — Issues flagged by 3+ personas (non-negotiable fixes)
   - Per issue: affected element, count of personas who flagged it, severity (critical/major/minor)

2. **Contradiction Map** — Where personas disagree
   - Per contradiction: the two positions, the industry split (e.g., "finance personas liked X but energy personas hated it"), recommendation for human judgment call

3. **Critical Bugs** — Rendering errors, broken functionality, missing data
   - These MUST be fixed before any other work. Fix → deploy → verify → continue

4. **Combined Scoring**
   - Average all persona Top-Down scores → Top-Down components
   - Average all persona Bottom-Up scores → Bottom-Up components
   - Weighted total: Top-Down × 0.40 + Bottom-Up × 0.60
   - Verdict: PASS / CONDITIONAL PASS / FAIL

5. **Priority-Ordered Fix List**
   - Rank by: severity × consensus count × fix effort (inverse)
   - Top 5 fixes named explicitly with element locations

**Output:** `aggregated-focus-group-report.md`

### Phase 4: INTEGRATION — Update & Deploy

**Goal:** Apply all fixes, update knowledge, and deploy.

**Sub-steps:**

1. **Fix critical bugs** (from Phase 3, step 3) — fix immediately, don't wait
2. **Apply priority fixes** (from Phase 3, step 5) — top-down, one at a time
3. **Update skill knowledge**
   - Add any new persona combinations to `proven-persona-combinations.md`
   - Add any new pitfalls or patterns to this skill
   - Update quality gate thresholds based on findings
4. **Update data** — fix any data quality issues found (wrong labels, stale data, missing sources)
5. **Deploy** — `bash /Users/alexstocchi/.hermes/scripts/gazzetta_deploy_to_gcs.sh`
6. **Verify deploy** — `gsutil cp gs://www.lagazzettadikyiv.com/index.html - | grep '<new-fix-marker>'`

**Output:** Deployed site + updated skill files + deploy verification log.

### Phase 5: QUALITY GATE — Verify & Close

**Goal:** Confirm fixes are live, no regressions, and close the cycle.

**Sub-steps:**

1. **Fresh Eyes review** — Spawn 2-3 Fresh Eyes personas (personas NOT used in Phase 2)
2. **Fix verification checklist:**
   - For each item in the priority list: Is the fix visible on the live site? Yes/No/Partial
   - Score fix effectiveness: 1-10 scale per fix
3. **Regression scan:**
   - Scan for any NEW issues introduced by fixes
   - Check: layout breaks, label consistency across containers, mobile rendering
4. **Cross-cycle knowledge integration:**
   - Save pipeline results to `data/quality_gates/history.jsonl`
   - Update quality gate thresholds
   - Archive the full pipeline output
5. **Close verdict:**
   - If all fixes at ≥ 8/10 and zero regressions: **PASS — CYCLE CLOSED**
   - If any fix < 7/10: loop back to Phase 4 with refined approach
   - If regression found: fix regression immediately, re-verify

**Output:** `quality-gate-verdict.md` + updated `history.jsonl`

---

## 5. PIPELINE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                        5-PHASE PIPELINE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PHASE 1: PRE-REVIEW                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐ │
│  │ Freshness Check  │───▶│ Source Audit     │───▶│ Live Site Verify │ │
│  └─────────────────┘    └──────────────────┘    └────────┬─────────┘ │
│                                                          │           │
│  PHASE 2: REVIEW (2 batches)                             ▼           │
│  ┌──────────────────────────────────────┐    ┌──────────────────────┐│
│  │ Batch 1: Initial (5 personas)        │───▶│ Batch 2: Targeted    ││
│  │ Finance + Industry + Contrarian      │    │ Fresh + Technical    ││
│  └──────────────────────────────────────┘    └──────────┬───────────┘│
│                                                          │           │
│  PHASE 3: POST-REVIEW                                    ▼           │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐ │
│  │ Consensus Catalog│───▶│ Contradiction Map│───▶│ Combined Scoring │ │
│  └─────────────────┘    └──────────────────┘    └────────┬─────────┘ │
│                                                          │           │
│  PHASE 4: INTEGRATION                                    ▼           │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐ │
│  │ Fix Critical     │───▶│ Apply Priority   │───▶│ Deploy + Verify  │ │
│  │ Bugs (immediate) │    │ Fixes + Update   │    │                  │ │
│  └─────────────────┘    └──────────────────┘    └────────┬─────────┘ │
│                                                          │           │
│  PHASE 5: QUALITY GATE                                   ▼           │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐ │
│  │ Fresh Eyes       │───▶│ Fix Verification │───▶│ PASS / LOOP     │ │
│  │ Review           │    │ + Regression     │    │ / FIX           │ │
│  └─────────────────┘    └──────────────────┘    └──────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. PERSONA ASSIGNMENT PROTOCOL

### 6.1 Review Types & Required Persona Mix

| Review Type | Finance Personas | Industry Personas | Generalist | Contrarian | Total |
|------------|-----------------|-------------------|------------|------------|-------|
| **Full Site Audit** | 2 (PM + Quant) | 4 (from 4 diff industries) | 2 | 2 | **10** |
| **Capital Flow Review** | 3 (PM + Trader + Quant) | 2 (energy + mining) | 1 | 1 | **7** |
| **Editorial Quality Audit** | 1 (Retail) | 2 (academia + defense) | 2 | 1 | **6** |
| **UX / Design Review** | 1 (Retail) | 2 (consumer + telecom) | 2 | 1 | **6** |
| **Data Product Review** | 3 (PM + Quant + PE) | 2 (legal + real estate) | 1 | 1 | **7** |
| **Crisis / Black Swan** | 2 (Degen + Gold) | 3 (defense + energy + shipping) | 1 | 1 | **7** |
| **Competitive Positioning** | 2 (PM + PE) | 2 (luxury + consumer) | 2 | 2 | **8** |

### 6.2 Rotating Selection (Cyclical)

Each full cycle should NOT reuse personas from the previous cycle if possible. Maintain a "persona usage log" in `data/persona-usage-log.jsonl`:

```json
{"date": "2026-06-07", "cycle": 42, "personas_used": ["PM", "Quant", "Energy Trader", "Defense Analyst", ...]}
```

If a persona hasn't been used in 3+ cycles, prioritize them for the next cycle.

---

## 7. SUCCESS CRITERIA

| KPI | Target | Measurement |
|-----|--------|-------------|
| **Persona coverage** | ≥ 35 unique personas used in the last 5 cycles | `persona-usage-log.jsonl` count |
| **Industry coverage** | ≥ 12 distinct industries per calendar month | Industry ID in aggregate reports |
| **Fix rate** | ≥ 80% of consensus issues resolved within 1 cycle | Phase 5 fix verification |
| **Regression rate** | < 10% of fixes introduce new issues | Phase 5 regression scan |
| **Combined score trend** | Increasing (or stable ≥ 8.0) over 5 cycles | Phase 3 combined score tracking |
| **Pipeline cycle time** | < 90 min from Phase 1 start to Phase 5 verdict | Timestamp log |
| **Persona diversity rate** | < 30% persona reuse between consecutive cycles | Usage log check |

---

## 8. REFERENCE FILES

| File | Contents |
|------|----------|
| `SKILL.md` | Master skill definition — pipeline, personas, evaluation methodology |
| `references/proven-persona-combinations.md` | Full 35+ persona roster + proven combinations |
| `references/retail-trader-persona-pack.md` | Retail trader personas with spawn patterns |
| `references/quality-gate-prompt-patterns.md` | Worked prompt templates for quality gates |
| `references/frontend-dom-timing-pitfalls.md` | DOM timing pitfalls and debugging patterns |
| `references/editorial-style-audit-dimensions.md` | Scoring rubric for editorial audits |
| `data/persona-usage-log.jsonl` | Log of which personas used in which cycle |
| `data/quality_gates/history.jsonl` | History of quality gate verdicts |

---

## 9. VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | June 2026 | Initial 20-persona finance/design focus group |
| 2.0.0 | June 2026 | 4-phase pipeline (Implementation → Maintenance → Remembering → Continuous) |
| **3.0.0** | **June 2026** | **35+ personas across 14 industries, top-down/bottom-up evaluation, 5-phase pipeline** |
