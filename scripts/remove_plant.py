#!/usr/bin/env python3
import yaml, argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()

    with open(args.file) as f:
        data = yaml.safe_load(f) or {'plants': []}

    filtered = [p for p in data.get('plants', []) if p['name'] != args.name]
    data['plants'] = filtered

    with open(args.file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

if __name__ == '__main__':
    main()
