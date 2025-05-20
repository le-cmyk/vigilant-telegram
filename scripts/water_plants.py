#!/usr/bin/env python3
import yaml, argparse, datetime, requests, os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    args = parser.parse_args()

    token = os.environ['TELEGRAM_BOT_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    today_str = datetime.date.today().isoformat()

    with open(args.file) as f:
        data = yaml.safe_load(f) or {'plants': []}

    for p in data.get('plants', []):
        last = datetime.datetime.fromisoformat(p['last_watered']).date()
        next_date = last + datetime.timedelta(days=p['frequency_days'])
        if next_date <= datetime.date.today():
            text = f"💧 Time to water **{p['name']}** (last: {p['last_watered']})"
            requests.get(
                f"https://api.telegram.org/bot{token}/sendMessage",
                params={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
            )
            p['last_watered'] = today_str

    with open(args.file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

if __name__ == '__main__':
    main()
