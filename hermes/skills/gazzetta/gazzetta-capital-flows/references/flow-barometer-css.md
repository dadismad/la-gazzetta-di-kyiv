# Capital Flow Barometer CSS Reference

Complete CSS for the 4-section institutional dashboard. Inserted before the mobile breakpoint section in `styles.css`.

## Section Containers

```css
.flow-dashboard-section { margin-bottom: 28px; }
.flow-section-title {
  font-family: "Playfair Display", Georgia, serif;
  font-size: 20px; font-weight: 600;
  color: #111827; margin: 0 0 4px 0;
}
.flow-section-subtitle {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 13px; color: #6B7280;
  margin: 0 0 16px 0; font-style: italic;
}
```

## Section 1: Global Flow Regime Card

```css
.flow-regime-card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-left: 4px solid #D4AF37;
  padding: 24px 28px; border-radius: 4px;
}
.regime-card-badge {
  display: inline-block;
  font-family: "Inter", sans-serif;
  font-size: 12px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 3px 10px; border-radius: 3px;
  margin-bottom: 12px;
}
.regime-card-badge.risk-on {
  background: rgba(5,150,105,0.10); color: #059669;
  border: 1px solid rgba(5,150,105,0.25);
}
.regime-card-badge.risk-off {
  background: rgba(220,38,38,0.08); color: #DC2626;
  border: 1px solid rgba(220,38,38,0.20);
}
.regime-card-badge.neutral {
  background: rgba(212,175,55,0.10); color: #B8860B;
  border: 1px solid rgba(212,175,55,0.25);
}
.regime-card-title {
  font-family: "Playfair Display", Georgia, serif;
  font-size: 24px; font-weight: 600;
  color: #111827; margin: 0 0 10px 0;
}
.regime-card-synthesis {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 15px; line-height: 1.6;
  color: #374151; margin: 0 0 20px 0;
  max-width: 680px;
}
.regime-card-stats {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 16px; border-top: 1px solid #E5E7EB;
  padding-top: 16px;
}
.regime-stat-value {
  font-family: "Inter", sans-serif;
  font-size: 22px; font-weight: 700; color: #111827;
}
.regime-stat-value.inflow { color: #059669; }
.regime-stat-value.outflow { color: #DC2626; }
.regime-stat-label {
  font-family: "Inter", sans-serif;
  font-size: 11px; font-weight: 500;
  color: #6B7280; text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

## Section 2: Net Sector Flows Grid

```css
.net-sector-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.sector-card {
  background: #FFFFFF; border: 1px solid #E5E7EB;
  padding: 16px; border-radius: 4px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.sector-card:hover {
  border-color: #D4AF37;
  box-shadow: 0 2px 8px rgba(212,175,55,0.10);
}
.sector-name {
  font-family: "Inter", sans-serif;
  font-size: 11px; font-weight: 600;
  color: #6B7280; text-transform: uppercase;
  letter-spacing: 0.05em;
}
.sector-net-value {
  font-family: "Inter", sans-serif;
  font-size: 18px; font-weight: 700;
  color: #111827; margin-bottom: 6px;
}
.sector-net-value.pos { color: #059669; }
.sector-net-value.neg { color: #DC2626; }
.sector-trend {
  font-family: "Inter", sans-serif;
  font-size: 11px; font-weight: 500;
}
.sector-trend.bullish { color: #059669; }
.sector-trend.bearish { color: #DC2626; }
.sector-trend.neutral { color: #6B7280; }
```

## Section 3: Positioning Cards

```css
.positioning-cards {
  display: flex; flex-direction: column; gap: 10px;
}
.positioning-card {
  background: #FFFFFF; border: 1px solid #E5E7EB;
  border-left: 3px solid #D4AF37;
  padding: 14px 18px; border-radius: 4px;
  display: flex; align-items: flex-start; gap: 12px;
}
.pos-card-connector {
  width: 8px; height: 8px; border-radius: 50%;
  background: #D4AF37; margin-top: 5px; flex-shrink: 0;
}
.pos-card-text {
  font-family: "Source Serif 4", Georgia, serif;
  font-size: 14px; line-height: 1.5;
  color: #374151; margin: 0;
}
```

## Section 4: Raw Telemetry Table

```css
.raw-telemetry-list {
  font-family: "Inter", sans-serif;
  max-height: 600px; overflow-y: auto;
  border: 1px solid #E5E7EB; border-radius: 4px;
}
.telemetry-row {
  display: grid;
  grid-template-columns: 70px 100px 60px 1fr 80px 110px;
  gap: 8px; align-items: center;
  padding: 5px 12px; font-size: 11px;
  border-bottom: 1px solid #F3F4F6;
  color: #6B7280;
}
.telemetry-row:last-child { border-bottom: none; }
.telemetry-row:nth-child(even) { background: #F9FAFB; }
.telemetry-row .tel-amount {
  font-weight: 600; color: #111827; font-size: 12px;
}
.telemetry-row .tel-dir {
  font-weight: 600; text-transform: uppercase; font-size: 10px;
}
.telemetry-row .tel-dir.inflow { color: #059669; }
.telemetry-row .tel-dir.outflow { color: #DC2626; }
.telemetry-row .tel-asset {
  font-weight: 500; color: #374151;
  text-transform: uppercase; font-size: 10px;
}
.telemetry-header {
  display: grid;
  grid-template-columns: 70px 100px 60px 1fr 80px 110px;
  gap: 8px; padding: 7px 12px;
  font-family: "Inter", sans-serif;
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
  color: #9CA3AF; background: #F9FAFB;
  border-bottom: 1px solid #E5E7EB;
  position: sticky; top: 0; z-index: 10;
}
```

## Mobile Breakpoint

```css
@media (max-width: 768px) {
  .regime-card-stats { grid-template-columns: repeat(2, 1fr); }
  .net-sector-grid { grid-template-columns: repeat(2, 1fr); }
  .telemetry-row, .telemetry-header {
    grid-template-columns: 60px 80px 1fr 70px;
  }
}
```
