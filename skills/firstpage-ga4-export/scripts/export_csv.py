import argparse
import csv
import json
from datetime import date
from pathlib import Path


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
            if 'rowCount' not in report or report['rowCount'] != len(rows):
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


def main():
    parser = argparse.ArgumentParser(description='Export Google organic daily sessions from complete GA4 reports.')
    parser.add_argument('--start', required=True, type=date.fromisoformat)
    parser.add_argument('--end', required=True, type=date.fromisoformat)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('reports', nargs='+', type=Path)
    args = parser.parse_args()
    if args.end < args.start:
        parser.error('The end date must be on or after the start date.')
    try:
        observed = collect(args.reports, args.start, args.end)
        if not observed:
            raise ValueError('No Google organic daily rows were returned.')
        with args.output.open('x', encoding='utf-8', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['Date', 'Sessions', 'Session source / medium'])
            for day, sessions in sorted(observed.items()):
                writer.writerow([day.isoformat(), sessions, 'google / organic'])
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f'{error}\n')
    missing = (args.end - args.start).days + 1 - len(observed)
    print(f'{args.output}: {len(observed)} daily rows, {missing} missing days.')


if __name__ == '__main__':
    main()
