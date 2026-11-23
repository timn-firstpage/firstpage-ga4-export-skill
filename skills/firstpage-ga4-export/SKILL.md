---
name: firstpage-ga4-export
description: Export daily Google organic sessions from an authorized GA4 property through the First Page MCP and save an upload-ready CSV for Traffic Forecasting. Use when the user asks for website organic traffic history or invokes this skill to export GA4 data.
---

# Export GA4 organic sessions

1. Find the requested property with the connected First Page MCP GA4 property search. Use the supplied property ID if available. If the site name matches multiple tracking properties, ask which one to use. The default scope is site-wide. Use the property's time zone for dates and honor any date range the user explicitly supplies.
2. Request the `date` and `sessionSourceMedium` dimensions with the `sessions` metric. Use an exact, case-insensitive `google / organic` filter if the tool supports it. Otherwise filter the returned rows locally. Use complete report rows. When the connector returns a preview or reports more rows than it returned, use its full-result facility if available. Otherwise split the inclusive date range into non-overlapping periods and retry smaller periods until each response is complete. Stop and explain if a complete response cannot be retrieved. Keep the date and source dimensions even on a prefiltered query. [GA4 API fields](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
3. If the user leaves dates open, start with the 24 calendar months ending at the last completed month. Require a returned Google organic sessions row for every calendar day. A returned zero counts as a day. If there is a gap, the next possible window ends in the month before the newest missing day. Check successively older windows and reuse any complete responses already fetched. If needed, use a site-wide `yearMonth` sessions report to locate the earliest available reporting month. If no complete window exists in the available history, say which dates were checked and ask whether to export a specific partial range.
4. Save `Date,Sessions,Session source / medium` in a UTF-8 CSV, sorted by date. Reject duplicate organic dates. For a user-specified range, leave missing dates out and report the count. For a homepage-only request, isolate sessions whose GA4 landing page matches the homepage path and disclose that scope. If the connector cannot isolate them reliably, explain the limitation.
5. Return a link to the CSV and state the property, selected dates and scope. If automatic selection moved the range back, mention that the latest period had gaps. Keep the raw response and CSV in the user's local or task workspace.

## Convert report JSON

Save each complete JSON response and run `python scripts/export_csv.py --start YYYY-MM-DD --end YYYY-MM-DD --output website-google-organic-daily.csv report.json [report-2.json ...]` from this skill's directory. Supply the bounds of the queried reports. Add `--latest-complete-window` for automatic date selection over the fetched history. Leave the flag out for dates the user chose explicitly. The script accepts a GA4 Data API report or a complete First Page MCP response and rejects previews.
