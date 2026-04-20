#!/usr/bin/env python
import urllib.request
import urllib.error

# Test root redirect
try:
    req = urllib.request.Request('http://localhost:8000/')
    req.add_header('Accept-Language', 'fr-FR')
    response = urllib.request.urlopen(req, timeout=5)
    print(f'Root URL returned: {response.status}')
except urllib.error.HTTPError as e:
    if e.code == 302:
        redirect_loc = e.headers.get('Location', 'No location')
        print(f'Root redirect confirmed: {e.code}')
        print(f'Redirects to: {redirect_loc}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')

print()

# Test /login/ redirect
try:
    req = urllib.request.Request('http://localhost:8000/login/')
    req.add_header('Accept-Language', 'en-US')
    response = urllib.request.urlopen(req, timeout=5)
    print(f'/login/ returned: {response.status}')
except urllib.error.HTTPError as e:
    if e.code == 302:
        redirect_loc = e.headers.get('Location', 'No location')
        print(f'/login/ redirect confirmed: {e.code}')
        print(f'Redirects to: {redirect_loc}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')

print()

# Test /fr/login/
try:
    response = urllib.request.urlopen('http://localhost:8000/fr/login/', timeout=5)
    print(f'/fr/login/ status: {response.status} ✓')
except urllib.error.HTTPError as e:
    print(f'/fr/login/ returned {e.code}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')

print()

# Test /en/login/
try:
    response = urllib.request.urlopen('http://localhost:8000/en/login/', timeout=5)
    print(f'/en/login/ status: {response.status} ✓')
except urllib.error.HTTPError as e:
    print(f'/en/login/ returned {e.code}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
