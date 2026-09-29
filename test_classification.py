import urllib.request
import json
import sys

def fetch(url):
    try:
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f'Error fetching {url}: {e}')
        sys.exit(1)

p_603293 = fetch('http://127.0.0.1:8000/projects/603293')
p_706724 = fetch('http://127.0.0.1:8000/projects/706724')

print('--- Project 603293 ---')
print(f"Monitoring Class: {p_603293['schedule_monitoring_class']}")
print(f"Monitoring Explanation: {p_603293['monitoring_explanation']}")

print('\n--- Project 706724 ---')
print(f"Monitoring Class: {p_706724['schedule_monitoring_class']}")
print(f"Monitoring Explanation: {p_706724['monitoring_explanation']}")

print('\n--- Test Analytics/Summary unchanged ---')
summary = fetch('http://127.0.0.1:8000/summary')
print(f"Summary earlier_revised_completion: {summary.get('earlier_revised_completion')}")
