import { Devvit } from '@devvit/public-api';

Devvit.configure({ redditAPI: true });

const POST_TITLE = 'Site Review — Gazzetta di Kyiv: OECD Dark Scenario, Iran-Gulf Convergence, Bet&Benefit Claims (June 3 Cycle)';
const POST_BODY = "# Site Review — Gazzetta di Kyiv, June 3 Cycle\n\nThe terminal is tracking 7 stories across geopolitics, macro, and tech convergence. The unifying thesis: **three stagflationary forces are converging while consensus prices them as independent risk buckets.**\n\n## Lead: OECD Calls the Recession That Consensus Won't Name\n\nThe OECD published a formal GDP contraction model conditional on Gulf energy disruption persisting through Q3 2026. On the same day: ECB Governing Council confirms 4.1% services inflation keeps rate rises on the table at 72% probability regardless of any Iran peace deal. Trump proposes 10% blanket forced-labour tariffs plus 25% on Brazil — despite the US running a trade surplus with Brazil.\n\n**Contradiction:** Markets price energy sector risk. The data shows energy inflation + tariff headwinds + monetary constraint = compounding stagflation, not a sectoral shock.\n\n## The Board\n\n- 🇰🇼 **Kuwait Airport Drone Strike** — Iranian drones hit Kuwait International Airport, civilian infrastructure threshold crossed (Kuwait MoI confirmed)\n- 🇯🇵 **Yen at 159.50** — Inside BOJ intervention territory. MOF's Suzuki flagged 160 as line. Last intervention Oct 2024, ¥9.8T\n- 🇺🇦 **Ukraine Bus Drone** — 7 civilians dead. Zelenskyy formally requests US missiles\n- 🤖 **Anthropic $1tn Valuation** — Instagram AI chatbot hacked same week. Security concentration risk compounding into the valuation layer\n\n## Bet&Benefit — 5 Asset Claims\n\n| Asset | Direction | Level | Strategy | Narrative-Driven |\n|-------|-----------|-------|----------|-----------------|\n| Gold (GC) | ⬆ | $3,450 | Accumulate on pullback | 60% |\n| EUR/USD | ⬆ | 1.1050 | Straddle into ECB, sell vol post | 45% |\n| Crude (CL) | ⬆ | $82.50 | Fade-the-move (65% win rate) | 75% |\n| Yen (JPY) | Fade | 155.00 | Counter-directional above 160 | 70% |\n| QQQ vs SPY | ⬇ | -5% | OTM puts on AI concentration | 55% |\n\nHighest conviction: crude fade — civilian infrastructure widens risk premium but structural surplus caps sustained moves above $85. The spike IS the trade.\n\n**Crypto read-through:** 26% of BTC move is narrative-driven — lowest of any tracked asset. The crowd hasn't priced the macro convergence into crypto yet. If dollar decline from tariff escalation + yen intervention materializes, BTC as asymmetric non-sovereign hedge.\n\n## Discussion\n\nThree stagflationary forces. Consensus pricing them as separate. What breaks first — European rates, credit spreads, or the yen carry trade? What single data point this week proves the OECD dark scenario wrong?\n\n*Full terminal: gazzetta-di-kyiv.com*";

Devvit.addMenuItem({
  label: 'Post Site Review',
  location: 'subreddit',
  onPress: async (_, context) => {
    const post = await context.reddit.submitPost({
      subredditName: 'LaGazzettadiKyiv',
      title: POST_TITLE,
      text: POST_BODY,
    });
    console.log(`Posted! ID: ${post.id}, URL: https://reddit.com${post.permalink}`);
  },
});

export default Devvit;
