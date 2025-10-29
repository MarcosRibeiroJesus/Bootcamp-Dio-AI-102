import requests
import json
import sys


def main():
    url = "http://localhost:8181/translate/url"
    payload = {
        "url": "https://dev.to/eric_dequ/steve-jobs-the-visionary-who-blended-spirituality-and-technology-3ppi",
        "lang": "português",
    }

    try:
        r = requests.post(url, json=payload, timeout=120)
    except Exception as e:
        print("Request failed:", e, file=sys.stderr)
        sys.exit(2)

    print(r.status_code)
    # Print headers (compact)
    print(dict(r.headers))

    # Try to pretty-print JSON response; fall back to raw text
    try:
        body = r.json()
        print(json.dumps(body, ensure_ascii=False, indent=2))
    except Exception:
        print(r.text)


if __name__ == "__main__":
    main()
