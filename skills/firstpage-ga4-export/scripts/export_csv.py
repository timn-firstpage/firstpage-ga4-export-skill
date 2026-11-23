import argparse
import csv
import json
import re
from calendar import monthrange
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlsplit


def reports(payload):
    envelope = payload.get('data', payload)
    if 'results' not in envelope:
        yield envelope
        return
    for item in envelope['results']:
        response = item['response']
        if response.get('successful') is False or 'data' not in response:
            raise ValueError('Expected a complete GA4 report, but the connector returned an error or preview.')
        yield response['data']


def collect(paths, start, end):
    observed = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding='utf-8-sig'))
        for report in reports(payload):
            rows = report.get('rows', [])
            if report.get('rowCount', 0) != len(rows):
                raise ValueError(f'{path.name} does not contain all GA4 rows.')
            dimensions = [item['name'] for item in report['dimensionHeaders']]
            metrics = [item['name'] for item in report['metricHeaders']]
            date_index = dimensions.index('date')
            source_index = dimensions.index('sessionSourceMedium')
            sessions_index = metrics.index('sessions')
            for row in rows:
                values = row['dimensionValues']
                if values[source_index]['value'].strip().casefold() != 'google / organic':
                    continue
                raw_day = values[date_index]['value']
                if len(raw_day) == 8 and raw_day.isdigit():
                    raw_day = f'{raw_day[:4]}-{raw_day[4:6]}-{raw_day[6:]}'
                day = date.fromisoformat(raw_day)
                sessions = int(row['metricValues'][sessions_index]['value'])
                if day in observed or not start <= day <= end or sessions < 0:
                    raise ValueError(f'Invalid or duplicate organic observation for {day}.')
                observed[day] = sessions
    return observed


def latest_complete_window(observed, start, end):
    one_day = timedelta(days=1)
    month = end.replace(day=1)
    if end.day < monthrange(end.year, end.month)[1]:
        month = (month - one_day).replace(day=1)
    counts = Counter(day.replace(day=1) for day in observed)
    consecutive_months = 0
    while month >= start:
        days = monthrange(month.year, month.month)[1]
        if counts[month] == days:
            if consecutive_months == 0:
                window_end = month.replace(day=days)
            consecutive_months += 1
            if consecutive_months == 24:
                return month, window_end
        else:
            consecutive_months = 0
        if month == start:
            break
        month = (month - one_day).replace(day=1)
    raise ValueError(f'No complete 24-month window was found between {start} and {end}.')


def export_name(site, scope, start, end):
    site = site.strip()
    host = urlsplit(site if '://' in site else f'//{site}').hostname
    if not host:
        raise ValueError('Enter a website URL or a property label such as property-123.')
    host = host.removeprefix('www.').encode('idna').decode('ascii').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', host).strip('-')[:100].rstrip('-')
    if not slug:
        raise ValueError('Enter a website URL or a property label such as property-123.')
    scope_label = 'Homepage' if scope == 'homepage' else 'Sitewide'
    return f'{slug}_GA4_Google-Organic_{scope_label}_{start}_to_{end}.csv'


def main():
    parser = argparse.ArgumentParser(description='Export Google organic daily sessions from complete GA4 reports.')
    parser.add_argument('--start', required=True, type=date.fromisoformat)
    parser.add_argument('--end', required=True, type=date.fromisoformat)
    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument('--output', type=Path, help='Write to a specific filename.')
    output_options.add_argument('--output-dir', type=Path, help='Save the automatically named CSV here.')
    parser.add_argument('--site', help='Website URL or property label used in the filename.')
    parser.add_argument('--scope', choices=['sitewide', 'homepage'], default='sitewide')
    parser.add_argument('--latest-complete-window', action='store_true',
                        help='Export only the newest 24 consecutive complete months in the queried range.')
    parser.add_argument('reports', nargs='+', type=Path)
    args = parser.parse_args()
    if args.end < args.start:
        parser.error('The end date must be on or after the start date.')
    if args.output is None and not args.site:
        parser.error('Supply --site for automatic naming or give a filename with --output.')
    try:
        observed = collect(args.reports, args.start, args.end)
        if not observed:
            raise ValueError('No Google organic daily rows were returned.')
        start, end = args.start, args.end
        if args.latest_complete_window:
            start, end = latest_complete_window(observed, start, end)
            observed = {day: sessions for day, sessions in observed.items() if start <= day <= end}
        output = args.output
        if output is None:
            output_dir = args.output_dir or Path('.')
            output = output_dir / export_name(args.site, args.scope, start, end)
        with output.open('x', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['Date', 'Sessions', 'Session source / medium'])
            for day, sessions in sorted(observed.items()):
                writer.writerow([day.isoformat(), sessions, 'google / organic'])
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f'{error}\n')
    missing = (end - start).days + 1 - len(observed)
    print(f'{output}: {start} to {end}, {len(observed)} daily rows, {missing} missing days.')


if __name__ == '__main__':
    main()
