import json
import base64

from pathlib import Path

from datetime import (
    datetime,
    timedelta
)


TOKEN_DIR = Path(
    "data/tokens"
)


# ------------------------------------------------
# DECODE JWT
# ------------------------------------------------

def decode_jwt(token):

    try:

        parts = token.split(".")

        if len(parts) != 3:

            return {}

        payload = parts[1]

        padding = "=" * (
            -len(payload) % 4
        )

        decoded = base64.urlsafe_b64decode(
            payload + padding
        )

        return json.loads(decoded)

    except Exception:

        return {}


# ------------------------------------------------
# PARSE TOKEN FILE
# ------------------------------------------------

def parse_token_file(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    access_token = data.get(
        "access_token",
        ""
    )

    jwt_data = decode_jwt(
        access_token
    )

    created = datetime.utcfromtimestamp(
        path.stat().st_mtime
    )

    expires_in = data.get(
        "expires_in",
        0
    )

    expires = (
        created +
        timedelta(seconds=expires_in)
    )

    remaining = (
        expires -
        datetime.utcnow()
    )

    valid = (
        remaining.total_seconds() > 0
    )

    scopes = jwt_data.get(
        "scp",
        ""
    )

    user = (

        jwt_data.get(
            "preferred_username"
        )

        or

        jwt_data.get(
            "upn"
        )

        or

        "unknown"
    )

    tenant = jwt_data.get(
        "tid",
        "unknown"
    )

    audience = jwt_data.get(
        "aud",
        "unknown"
    )

    return {

        "file":
            path.name,

        "app":
            path.name.split("_")[0],

        "user":
            user,

        "tenant":
            tenant,

        "audience":
            audience,

        "created":
            created,

        "expires":
            expires,

        "remaining":
            remaining,

        "valid":
            valid,

        "scopes":
            scopes,

        "has_refresh":
            "refresh_token" in data,

        "raw":
            data
    }


# ------------------------------------------------
# LIST TOKENS
# ------------------------------------------------

def list_tokens():

    files = sorted(
        TOKEN_DIR.glob("*.json")
    )

    if not files:

        print(
            "[-] No saved tokens found"
        )

        return

    HIGH_VALUE_SCOPES = [

        "Files.ReadWrite.All",
        "Files.ReadWrite",
        "Files.Read.All",

        "Mail.ReadWrite",
        "Mail.Send",

        "Sites.ReadWrite.All",

        "Directory.ReadWrite.All",

        "User.ReadWrite.All",

        "Group.ReadWrite.All",

        "Notes.ReadWrite.All",

        "Tasks.ReadWrite"
    ]

    parsed = []

    for path in files:

        info = parse_token_file(
            path
        )

        scopes = info[
            "scopes"
        ].split()

        interesting = [

            s for s in scopes
            if s in HIGH_VALUE_SCOPES
        ]

        info[
            "interesting_scopes"
        ] = (

            ", ".join(interesting)

            if interesting

            else "None"
        )

        parsed.append(info)

    # ------------------------------------------------
    # TABLE
    # ------------------------------------------------

    print()

    print(
        "┌────────────────────────────────────┬──────────┬──────────────────────────┬───────┬─────────┬──────────────┬──────────────────────────────────────┐"
    )

    print(
        "│ Session File                       │ App      │ User                     │ Valid │ Refresh │ Time Left    │ High Value Permissions              │"
    )

    print(
        "├────────────────────────────────────┼──────────┼──────────────────────────┼───────┼─────────┼──────────────┼──────────────────────────────────────┤"
    )

    for info in parsed:

        valid = (
            "YES"
            if info["valid"]
            else "NO"
        )

        refresh = (
            "YES"
            if info["has_refresh"]
            else "NO"
        )

        if info["valid"]:

            remaining = str(
                info["remaining"]
            ).split(".")[0]

        else:

            remaining = "EXPIRED"

        perms = info[
            "interesting_scopes"
        ]

        if len(perms) > 36:

            perms = perms[:33] + "..."

        session_file = info[
            "file"
        ]

        if len(session_file) > 34:

            session_file = (
                session_file[:31] + "..."
            )

        print(
            f"│ "
            f"{session_file:<34} │ "
            f"{info['app'][:8]:<8} │ "
            f"{info['user'][:24]:<24} │ "
            f"{valid:<5} │ "
            f"{refresh:<7} │ "
            f"{remaining[:12]:<12} │ "
            f"{perms:<36} │"
        )

    print(
        "└────────────────────────────────────┴──────────┴──────────────────────────┴───────┴─────────┴──────────────┴──────────────────────────────────────┘"
    )

    print()


# ------------------------------------------------
# GET TOKEN BY FILE
# ------------------------------------------------

def get_token_from_file(path):

    info = parse_token_file(
        Path(path)
    )

    return info["raw"].get(
        "access_token"
    )


# ------------------------------------------------
# GET LATEST TOKEN
# ------------------------------------------------

def get_latest_token(app="copilot"):

    files = sorted(
        TOKEN_DIR.glob(f"{app}_*.json"),
        reverse=True
    )

    if not files:

        return None

    latest = files[0]

    return get_token_from_file(
        latest
    )