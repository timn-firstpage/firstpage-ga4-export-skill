# First Page GA4 Export Skill

Export daily Google organic sessions to a CSV for Traffic Forecasting using your connected First Page MCP. You need access to the GA4 property you want to export.

## Install in Codex

Ask Codex to run `$skill-installer` with this folder URL, then start a new session.

```text
https://github.com/timn-firstpage/firstpage-ga4-export-skill/tree/main/skills/firstpage-ga4-export
```

You can also copy the `skills/firstpage-ga4-export` folder into your Codex skills directory. [Installing Codex skills](https://developers.openai.com/api/reference/cli)

## Export

Paste the following prompt in Codex. Add a website or GA4 property ID if you know it.

```text
Use $firstpage-ga4-export with my connected First Page MCP. Find the newest 24 consecutive complete months with daily google / organic sessions for my site. Save an upload-ready CSV with Date, Sessions, and Session source / medium. Return the file link and the dates you selected. Ask me which GA4 property to use if it is unclear.
```

The skill looks back when the latest months have missing days. Include start and end dates in your request if you prefer to export a specific period. Upload the generated CSV in Traffic Forecasting under Organic forecast.

Export speed depends on the connector. Server-side filtering or access to the complete response lets the skill fetch larger date ranges. When only inline results are available, the skill sizes each request using the site's observed row count and reuses completed chunks during retries.
