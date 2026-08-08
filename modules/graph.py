import requests
import base64
import json
import time

GRAPH = "https://graph.microsoft.com/v1.0"

TOKEN_SCOPES = set()


def graph_get(endpoint, token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"{GRAPH}{endpoint}"

    results = []

    while url:

        r = requests.get(
            url,
            headers=headers
        )

        if r.status_code != 200:

            print(
                f"[GRAPH ERROR] "
                f"{r.status_code}"
            )

            print(r.text)

            return None

        data = r.json()

        if "value" in data:

            results.extend(data["value"])

        else:

            return data

        url = data.get("@odata.nextLink")

    return {"value": results}


def decode_token(token):

    global TOKEN_SCOPES

    payload = token.split(".")[1]

    payload += "=" * (-len(payload) % 4)

    decoded = json.loads(
        base64.urlsafe_b64decode(payload)
    )

    scopes = decoded.get("scp", "")

    TOKEN_SCOPES = set(
        scopes.split()
    )

    print("\n=== TOKEN INFO ===")

    print(
        f"Tenant ID: "
        f"{decoded.get('tid')}"
    )

    print(
        f"Audience: "
        f"{decoded.get('aud')}"
    )

    exp = decoded.get("exp")

    if exp:

        print(
            f"Expires: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))}"
        )

    print("\n=== TOKEN SCOPES ===")

    for s in TOKEN_SCOPES:

        print(s)


def has_scope(scope):

    return scope in TOKEN_SCOPES