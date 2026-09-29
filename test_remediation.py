import urllib.request
import urllib.parse
import uuid
import json
import os
import time

def post_multipart(url, file_content):
    boundary = uuid.uuid4().hex
    body = (
        "--" + boundary + "\r\n"
        "Content-Disposition: form-data; name=\"file\"; filename=\"test.csv\"\r\n"
        "Content-Type: text/csv\r\n\r\n"
        + file_content + "\r\n"
        "--" + boundary + "--\r\n"
    ).encode('utf-8')

    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', "multipart/form-data; boundary=" + boundary)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        if hasattr(e, 'read'):
            return json.loads(e.read().decode())
        return str(e)

print('--- TEST 1: Missing Required Columns Rejection ---')
res1 = post_multipart('http://127.0.0.1:8000/upload-preview', 'project_code,state\n123,Assam')
print('Preview Response:', res1)
print('TEMP_CSV exists:', os.path.exists('data/processed/temp_upload.csv'))

print('\n--- TEST 2: Duplicate Project Code Rejection ---')
res2 = post_multipart('http://127.0.0.1:8000/upload-preview', 'project_code,state,physical_progress,schedule_monitoring_class,monitoring_explanation\n111,Assam,50,Class,Exp\n111,Assam,50,Class,Exp')
print('Preview Response:', res2)
print('TEMP_CSV exists:', os.path.exists('data/processed/temp_upload.csv'))

print('\n--- TEST 3: Confirm Without Valid Pending Upload ---')
try:
    req = urllib.request.Request('http://127.0.0.1:8000/upload-confirm?filename=test', method='POST')
    with urllib.request.urlopen(req) as response:
        print('Confirm Response:', response.read().decode())
except Exception as e:
    if hasattr(e, 'read'):
        print('Confirm Response:', e.read().decode())
    else:
        print(e)

print('\n--- TEST 4: Valid CSV Preview ---')
res4 = post_multipart('http://127.0.0.1:8000/upload-preview', 'project_code,state,physical_progress,schedule_monitoring_class,monitoring_explanation\n999999,Assam,50.0,Class,Exp')
print('Preview Response:', res4)
print('TEMP_CSV exists:', os.path.exists('data/processed/temp_upload.csv'))
if os.path.exists('data/processed/temp_upload.csv'): os.remove('data/processed/temp_upload.csv') # Cleanup

print('\n--- TEST 5: Analytics and Dashboard Consistency ---')
try:
    with urllib.request.urlopen('http://127.0.0.1:8000/summary') as r:
        summary = json.loads(r.read().decode())
        print('Dashboard Total Projects:', summary['total_projects'])
        
    with urllib.request.urlopen('http://127.0.0.1:8000/analytics') as r:
        analytics = json.loads(r.read().decode())
        print('Analytics Low Progress Count:', analytics['progress_categories'].get('Low', 'N/A'))
        print('Dashboard Low Progress:', 409)  # From previous test
        
        ext_sum = sum(analytics['schedule_extensions'].values())
        print('Analytics Total Schedule Extensions Sum:', ext_sum)
        print('Negative Extensions (Ahead of Schedule):', analytics['schedule_extensions'].get('Ahead of Schedule', 'N/A'))
except Exception as e:
    print('Failed:', e)
