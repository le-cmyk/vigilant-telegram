#!/usr/bin/env python3
import yaml, argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--start', required=True)
    parser.add_argument('--freq', type=int, required=True)
    args = parser.parse_args()

    with open(args.file) as f:
        data = yaml.safe_load(f) or {'plants': []}

    data.setdefault('plants', []).append({
        'name': args.name,
        'last_watered': args.start,
        'frequency_days': args.freq
    })

    with open(args.file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

if __name__ == '__main__':
    main()
