import csv
import time
import requests

GRAPH = "https://graph.microsoft.com/v1.0"

REQUEST_TIMEOUT = 20


# ------------------------------------------------
# GRAPH HELPER
# ------------------------------------------------

def graph_get(endpoint, token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"{GRAPH}{endpoint}"

    results = []

    while url:

        r = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        if r.status_code != 200:

            return None

        data = r.json()

        if "value" in data:

            results.extend(
                data["value"]
            )

        else:

            return data

        url = data.get("@odata.nextLink")

    return {"value": results}


# ------------------------------------------------
# USERS
# ------------------------------------------------

def list_users(token):

    print("\n=== TENANT USERS ===")

    data = graph_get(
        "/users?$top=999",
        token
    )

    if not data:

        print(
            "[-] Failed enumerating users"
        )

        return []

    users = []

    rows = []

    for user in data.get("value", []):

        display = user.get(
            "displayName"
        )

        upn = user.get(
            "userPrincipalName"
        )

        print(
            f"{display} | {upn}"
        )

        users.append(upn)

        rows.append([
            display,
            upn
        ])

    with open(
        "tenant_users.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "Name",
            "UPN"
        ])

        writer.writerows(rows)

    print(
        "\n[+] Saved tenant_users.csv"
    )

    return users


# ------------------------------------------------
# SHAREPOINT SITES
# ------------------------------------------------

def list_sites(token):

    print(
        "\n=== SHAREPOINT SITES ==="
    )

    data = graph_get(
        "/sites?search=*",
        token
    )

    if not data:

        print(
            "[-] SharePoint site enumeration blocked"
        )

        return

    for site in data.get("value", []):

        print(
            site.get("webUrl")
        )


# ------------------------------------------------
# SEARCH FILES
# ------------------------------------------------

def search_files(
    token,
    keyword
):

    print(
        f"\n=== SEARCH: {keyword} ==="
    )

    data = graph_get(
        f"/me/drive/root/search(q='{keyword}')",
        token
    )

    if not data:

        print(
            "[-] Search failed"
        )

        return

    for item in data.get("value", []):

        print(
            item.get("name")
        )


# ------------------------------------------------
# UPLOAD TEST FILE
# ------------------------------------------------

def upload_test_file(
    token,
    filename="sharing_test.txt"
):

    headers = {

        "Authorization":
            f"Bearer {token}",

        "Content-Type":
            "text/plain"
    }

    content = (
        "This is a harmless "
        "sharing configuration test."
    )

    upload_url = (
        f"{GRAPH}/me/drive/root:/"
        f"{filename}:/content"
    )

    print(
        "\n[*] Uploading sharing test file..."
    )

    r = requests.put(
        upload_url,
        headers=headers,
        data=content.encode(),
        timeout=REQUEST_TIMEOUT
    )

    if r.status_code not in [200, 201]:

        print(
            "[-] Upload failed"
        )

        return None

    print(
        "[+] Upload successful"
    )

    return r.json()


# ------------------------------------------------
# TEST ANONYMOUS LINK CREATION
# ------------------------------------------------

def test_anonymous_link_creation(
    token,
    item_id
):

    headers = {

        "Authorization":
            f"Bearer {token}",

        "Content-Type":
            "application/json"
    }

    url = (
        f"{GRAPH}/me/drive/items/"
        f"{item_id}/createLink"
    )

    body = {

        "type":
            "view",

        "scope":
            "anonymous"
    }

    print(
        "\n[*] Testing anonymous sharing..."
    )

    r = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=REQUEST_TIMEOUT
    )

    if r.status_code in [200, 201]:

        print(
            "[+] Anonymous sharing: ALLOWED"
        )

        return True

    print(
        "[+] Anonymous sharing: BLOCKED"
    )

    return False


# ------------------------------------------------
# TEST ORG LINK CREATION
# ------------------------------------------------

def test_org_link_creation(
    token,
    item_id
):

    headers = {

        "Authorization":
            f"Bearer {token}",

        "Content-Type":
            "application/json"
    }

    url = (
        f"{GRAPH}/me/drive/items/"
        f"{item_id}/createLink"
    )

    body = {

        "type":
            "view",

        "scope":
            "organization"
    }

    print(
        "\n[*] Testing organization sharing..."
    )

    r = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=REQUEST_TIMEOUT
    )

    if r.status_code in [200, 201]:

        print(
            "[+] Organization sharing: ALLOWED"
        )

        return True

    print(
        "[+] Organization sharing: BLOCKED"
    )

    return False


# ------------------------------------------------
# TEST EXTERNAL SHARING
# ------------------------------------------------

def test_external_invite(
    token,
    item_id,
    external_email
):

    headers = {

        "Authorization":
            f"Bearer {token}",

        "Content-Type":
            "application/json"
    }

    url = (
        f"{GRAPH}/me/drive/items/"
        f"{item_id}/invite"
    )

    body = {

        "recipients": [
            {
                "email": external_email
            }
        ],

        "requireSignIn":
            False,

        "sendInvitation":
            True,

        "roles": [
            "read"
        ]
    }

    print(
        "\n[*] Testing external sharing..."
    )

    r = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=REQUEST_TIMEOUT
    )

    if r.status_code in [200, 201]:

        print(
            "[+] External sharing: ALLOWED"
        )

        return True

    print(
        "[+] External sharing: BLOCKED"
    )

    return False


# ------------------------------------------------
# MAIN
# ------------------------------------------------

if __name__ == "__main__":

    TOKEN = "PASTE_TOKEN"

    # ---------------------------------
    # ENUMERATION
    # ---------------------------------

    list_users(TOKEN)

    list_sites(TOKEN)

    search_files(
        TOKEN,
        "password"
    )

    # ---------------------------------
    # SHARING TESTS
    # ---------------------------------

    uploaded = upload_test_file(
        TOKEN
    )

    if uploaded:

        item_id = uploaded["id"]

        print(
            "\n[*] Waiting for SharePoint indexing..."
        )

        time.sleep(5)

        # ---------------------------------
        # ANONYMOUS LINK TEST
        # ---------------------------------

        test_anonymous_link_creation(
            TOKEN,
            item_id
        )

        # ---------------------------------
        # ORG LINK TEST
        # ---------------------------------

        test_org_link_creation(
            TOKEN,
            item_id
        )

        # ---------------------------------
        # EXTERNAL SHARE TEST
        # ---------------------------------

        test_external_invite(
            TOKEN,
            item_id,
            "your_external_test@gmail.com"
        )