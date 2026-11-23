---
name: firstpage-ga4-export
description: Export daily Google organic sessions from an authorized GA4 property through the First Page MCP and save an upload-ready CSV for Traffic Forecasting. Use when the user asks for website organic traffic history or invokes this skill to export GA4 data.
---

# Export GA4 organic sessions

1. Find the requested property with the connected First Page MCP GA4 property search. Use the supplied property ID if available. If the site name matches multiple tracking properties, ask which one to use. The default scope is site-wide. Use the property's time zone for dates and honor any date range the user explicitly supplies.
2. If the user leaves dates open, start with the 24 calendar months ending at the last completed month. Require a returned Google organic sessions row for every calendar day. A returned zero counts as a day. If there is a gap, the next possible window ends in the month before the newest missing day. Check successively older windows, fetching only dates not covered by complete responses already available. If needed, use a site-wide `yearMonth` sessions report to locate the earliest available reporting month. If no complete window exists, say which dates were checked and ask whether to export a specific partial range.
3. Fetch `date`, `sessionSourceMedium` and `sessions` using the report strategy below. Save `Date,Sessions,Session source / medium` in a UTF-8 CSV sorted by date. Reject duplicate organic dates. For a user-specified range, leave missing dates out and report the count. For a homepage-only request, isolate sessions whose GA4 landing page matches the homepage path and disclose that scope. If the connector cannot isolate them reliably, explain the limitation.
4. Return a link to the CSV and state the property, selected dates and scope. If automatic selection moved the range back, mention that the latest period had gaps. Keep downloaded data in the user's local or task workspace.

## Fetch the report efficiently

- Inspect the connected report tool before starting. If it supports server-side filtering, apply an exact, case-insensitive `sessionSourceMedium = google / organic` filter and keep the source dimension in the result. If the runtime can retrieve the connector's full report files, use this with the largest useful range. If the filtered response is still a preview, retry smaller ranges with the same filter. A preview alone is insufficient. [GA4 report filters](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
- When the tool lacks filters and the runtime cannot read report files, skip an unfiltered two-year request. Fetch the newest 14 days as the first chunk, then size the remaining non-overlapping date chunks using the number of rows per day in that complete response. Aim for about 280 rows per chunk and set the tool's row limit above that. For example, a site returning 17 rows per day can use 16-day chunks. If a chunk is incomplete, retry only that chunk with a shorter date range and reduce the size of unrequested chunks as needed. A complete response has all rows indicated by the report's row count.
- Group independent chunks when the tool runner supports parallel calls. If programmatic tool-result processing is available, validate the full row counts there and save only the exact `google / organic` rows needed by the CSV builder. Save completed chunks as they arrive, with their report dates, property and scope, so a retry can resume the same export. Reuse only verified chunks for the same property, dates, scope and filter. Fetch again if the user requests fresh data.
- When chunking will take a while, tell the user which property and dates are being checked before fetching the full range. Report progress by dates or chunks completed, and explain any switch to older history.

## Convert report JSON

Save each complete JSON response and run `python scripts/export_csv.py --start YYYY-MM-DD --end YYYY-MM-DD --output website-google-organic-daily.csv report.json [report-2.json ...]` from this skill's directory. Supply the bounds of the queried reports. Add `--latest-complete-window` for automatic date selection over the fetched history. Leave the flag out for dates the user chose explicitly. The script accepts a GA4 Data API report or a complete First Page MCP response and rejects previews.
