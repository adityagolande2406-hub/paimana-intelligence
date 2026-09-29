import urllib.request
import json
import urllib.error

def fetch(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {'status_code': e.code, 'detail': json.loads(e.read().decode())}
    except Exception as e:
        return str(e)

base = 'http://127.0.0.1:8000'

print('--- Testing Risk Endpoints ---')
for code in [706724, 706718, 612793, 603293, 999999]:
    res = fetch(f'{base}/projects/{code}/risk')
    if 'status_code' in res:
        print(f"{code}: HTTP {res['status_code']} - {res['detail']}")
    else:
        print(f"{code}: {res['schedule_assessment']}, {res['financial_assessment']}, {res['progress_assessment']}")

print('\n--- Verifying Core Endpoints ---')
print('Summary keys:', list(fetch(f'{base}/summary').keys()))
print('Analytics keys:', list(fetch(f'{base}/analytics').keys()))
print('Projects count:', fetch(f'{base}/projects?limit=1').get('total'))
print('Health:', fetch(f'{base}/health'))
