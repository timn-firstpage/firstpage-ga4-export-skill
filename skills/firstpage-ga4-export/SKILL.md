---
name: firstpage-ga4-export
description: Export daily Google organic sessions from an authorized GA4 property through the First Page MCP and save an upload-ready CSV for Traffic Forecasting. Use when the user asks for website organic traffic history or invokes this skill to export GA4 data.
---

# Export GA4 organic sessions

1. Find the requested property with the connected First Page MCP GA4 property search. Use the supplied property ID if available. If the site name matches multiple tracking properties, ask which one to use. Use the requested date range or the latest 24 complete calendar months in the property time zone. The default scope is site-wide.
2. Request the `date` and `sessionSourceMedium` dimensions with the `sessions` metric. Use an exact, case-insensitive `google / organic` filter if the tool supports it. Otherwise filter the returned rows locally. Use complete report rows. When the connector returns a preview or reports more rows than it returned, use its full-result facility if available. Otherwise split the inclusive date range into non-overlapping periods and retry smaller periods until each response is complete. Stop and explain if a complete response cannot be retrieved. Keep the date and source dimensions even on a prefiltered query. [GA4 API fields](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
3. Save `Date,Sessions,Session source / medium` in a UTF-8 CSV, sorted by date. Use the real Google organic count for each returned day. Leave absent dates out and report how many are missing. Reject duplicate organic dates. If the user requests homepage-only data, use a GA4 landing page filter that matches their homepage path and disclose the scope. Pause if the available connector cannot apply that filter or reliably isolate homepage sessions.
4. Return a link to the actual CSV and state which property, dates and scope were used. Keep the raw response and CSV in the user's local or task workspace. Use a short file name such as `website-google-organic-daily.csv`.

## Convert report JSON

If the tool returns JSON, save each complete response and run `python scripts/export_csv.py --start YYYY-MM-DD --end YYYY-MM-DD --output website-google-organic-daily.csv report.json [report-2.json ...]` from this skill's directory. The script accepts a GA4 Data API report or the complete First Page MCP response envelope. A report preview produces an error.
