"""Live HTTP check. Sends OFF commands only; never energizes relay channels."""
import argparse
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    args = parser.parse_args()
    base = args.url.rstrip('/')
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'build/manifest.json').read_text())
    checks = []

    def request(path, fields=None, expected=200):
        data = None if fields is None else urllib.parse.urlencode(fields).encode()
        req = urllib.request.Request(base + path, data=data)
        try:
            response = urllib.request.urlopen(req, timeout=5)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = response.read()
            assert response.status == expected, (path, response.status, body)
        return body

    status = json.loads(request('/api/status'))
    assert status['version'] == manifest['version'] and status['buildUTC'] == manifest['buildUTC']
    assert status['ready'] and status['staConnected'] and status['mcpAddress'] == '0x20'
    assert status['watchdogPin'] == 2 and status['watchdogPeriodMs'] == 25
    checks.append('live identity, STA, MCP readiness and watchdog config')
    assert b'<title>JIN Relay Control</title>' in request('/')
    checks.append('root HTML HTTP 200')
    # Start and end all OFF, including cleanup if a later assertion fails.
    try:
        assert json.loads(request('/api/all', {'state': '0'}))['mask'] == 0
        for channel in range(1, 9):
            assert json.loads(request('/api/relay', {'channel': str(channel), 'state': '0'}))['mask'] == 0
        checks.append('all eight OFF commands and MCP readback')
        for fields in ({'channel': '0', 'state': '1'}, {'channel': '9', 'state': '1'},
                       {'channel': '1x', 'state': '1'}, {'channel': '1', 'state': '2'},
                       {'channel': '1'}, {'channel': '1', 'state': '0', 'extra': '1'}):
            request('/api/relay', fields, 400)
        request('/api/all', {'state': '2'}, 400)
        request('/api/relay', expected=404)
        request('/missing', expected=404)
        checks.append('seven malformed POSTs and two invalid GET routes rejected')
        previous = status['uptimeMs']
        for _ in range(20):
            status = json.loads(request('/api/status'))
            assert status['ready'] and status['mask'] == 0 and status['uptimeMs'] >= previous
            previous = status['uptimeMs']
            time.sleep(0.15)
        checks.append('20 status samples without fault/reset; final mask=0')
    finally:
        request('/api/all', {'state': '0'})
    print(json.dumps({'result': 'PASS', 'checks': checks, 'version': status['version'],
                      'buildUTC': status['buildUTC'], 'finalMask': status['mask']}, indent=2))

if __name__ == '__main__':
    main()
