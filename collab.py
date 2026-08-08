import requests
import os

GRAPH = "https://graph.microsoft.com/v1.0"


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
            headers=headers
        )

        # ---------------------------------
        # ERROR HANDLING
        # ---------------------------------

        if r.status_code == 401:

            print(
                "[-] Unauthorized or expired token"
            )

            return None

        if r.status_code == 403:

            print(
                "[-] Access denied / missing scope"
            )

            return None

        if r.status_code != 200:

            print(
                f"[GRAPH ERROR] "
                f"{r.status_code}"
            )

            try:

                print(r.json())

            except Exception:

                print(r.text)

            return None

        data = r.json()

        if "value" in data:

            results.extend(
                data["value"]
            )

        else:

            return data

        url = data.get(
            "@odata.nextLink"
        )

    return {"value": results}


# ------------------------------------------------
# DOWNLOAD DRIVE ITEM
# ------------------------------------------------

def download_drive_item(
    token,
    item,
    output_dir="downloads"
):

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    name = item.get(
        "name",
        "unknown.bin"
    )

    item_id = item.get("id")

    # ---------------------------------
    # DIRECT DOWNLOAD URL
    # ---------------------------------

    download_url = item.get(
        "@microsoft.graph.downloadUrl"
    )

    # ---------------------------------
    # FALLBACK GRAPH CONTENT API
    # ---------------------------------

    if not download_url:

        download_url = (
            f"{GRAPH}/me/drive/items/"
            f"{item_id}/content"
        )

    print(
        f"[DOWNLOAD] {name}"
    )

    r = requests.get(
        download_url,
        headers=headers,
        allow_redirects=True
    )

    if r.status_code != 200:

        print(
            f"[-] Failed downloading "
            f"{name}: {r.status_code}"
        )

        try:

            print(r.json())

        except Exception:

            print(r.text)

        return False

    save_path = os.path.join(
        output_dir,
        name
    )

    with open(save_path, "wb") as f:

        f.write(r.content)

    print(
        f"[+] Saved: {save_path}"
    )

    return True


# ------------------------------------------------
# RECENT FILES
# ------------------------------------------------

def recent_files(
    token,
    auto_download=False
):

    print(
        "\n=== RECENT FILES ==="
    )

    data = graph_get(
        "/me/drive/recent",
        token
    )

    if not data:

        return []

    files = []

    for item in data.get("value", []):

        name = item.get(
            "name",
            "unknown"
        )

        web_url = item.get(
            "webUrl",
            "unknown"
        )

        modified = item.get(
            "lastModifiedDateTime",
            "unknown"
        )

        print(
            f"[RECENT] {name}"
        )

        print(
            f"  Modified : "
            f"{modified}"
        )

        print(
            f"  URL      : "
            f"{web_url}"
        )

        # ---------------------------------
        # AUTO DOWNLOAD
        # ---------------------------------

        if auto_download:

            try:

                download_drive_item(
                    token,
                    item
                )

            except Exception as e:

                print(
                    f"[-] Download error: {e}"
                )

        print()

        files.append({

            "name":
                name,

            "modified":
                modified,

            "url":
                web_url,

            "raw":
                item
        })

    print(
        f"[+] Recent files: "
        f"{len(files)}"
    )

    return files


# ------------------------------------------------
# SHARED WITH ME
# ------------------------------------------------

def shared_with_me(
    token,
    auto_download=False
):

    print(
        "\n=== SHARED WITH ME ==="
    )

    data = graph_get(
        "/me/drive/sharedWithMe",
        token
    )

    if not data:

        return []

    items = []

    for item in data.get("value", []):

        name = item.get(
            "name",
            "unknown"
        )

        remote = item.get(
            "remoteItem",
            {}
        )

        web_url = remote.get(
            "webUrl",
            "unknown"
        )

        owner = (
            remote.get(
                "createdBy",
                {}
            )
            .get(
                "user",
                {}
            )
            .get(
                "displayName",
                "unknown"
            )
        )

        print(
            f"[SHARED] {name}"
        )

        print(
            f"  Owner : {owner}"
        )

        print(
            f"  URL   : {web_url}"
        )

        # ---------------------------------
        # AUTO DOWNLOAD
        # ---------------------------------

        if auto_download:

            try:

                download_drive_item(
                    token,
                    remote
                )

            except Exception as e:

                print(
                    f"[-] Download error: {e}"
                )

        print()

        items.append({

            "name":
                name,

            "owner":
                owner,

            "url":
                web_url,

            "raw":
                item
        })

    print(
        f"[+] Shared items: "
        f"{len(items)}"
    )

    return items


# ------------------------------------------------
# NOTEBOOKS
# ------------------------------------------------

def enumerate_notebooks(token):

    print(
        "\n=== ONENOTE NOTEBOOKS ==="
    )

    data = graph_get(
        "/me/onenote/notebooks",
        token
    )

    if not data:

        return []

    notebooks = []

    for notebook in data.get("value", []):

        name = notebook.get(
            "displayName",
            "unknown"
        )

        web_url = notebook.get(
            "links",
            {}
        ).get(
            "oneNoteWebUrl",
            {}
        ).get(
            "href",
            "unknown"
        )

        print(
            f"[NOTEBOOK] "
            f"{name}"
        )

        print(
            f"  URL : "
            f"{web_url}"
        )

        print()

        notebooks.append({

            "name":
                name,

            "url":
                web_url,

            "raw":
                notebook
        })

    print(
        f"[+] Notebooks: "
        f"{len(notebooks)}"
    )

    return notebooks


# ------------------------------------------------
# SUMMARY
# ------------------------------------------------

def collaboration_summary(token):

    print(
        "\n================================="
    )

    print(
        "COLLABORATION DISCOVERY SUMMARY"
    )

    print(
        "================================="
    )

    shared = shared_with_me(
        token,
        auto_download=True
    )

    recent = recent_files(
        token,
        auto_download=True
    )

    notebooks = enumerate_notebooks(
        token
    )

    print(
        "\n================================="
    )

    print(
        "SUMMARY"
    )

    print(
        "================================="
    )

    print(
        f"Shared Items     : "
        f"{len(shared)}"
    )

    print(
        f"Recent Files     : "
        f"{len(recent)}"
    )

    print(
        f"OneNote Books    : "
        f"{len(notebooks)}"
    )

    print(
        "\n[+] Collaboration discovery completed"
    )


# ------------------------------------------------
# MAIN
# ------------------------------------------------

if __name__ == "__main__":

    TOKEN = "PASTE_TOKEN"

    collaboration_summary(
        TOKEN
    )