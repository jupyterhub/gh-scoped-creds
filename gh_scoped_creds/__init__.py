import argparse
import os
import sys
import time

import requests


def do_authenticate_device_flow(client_id, in_jupyter=False):
    """
    Authenticate user with given GitHub app using GitHub OAuth Device flow

    https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#device-flow
    describes what happens here.

    Returns an access_code and the number of seconds it expires in.
    access_code will have scopes defined in the GitHub app
    """
    verification_resp = requests.post(
        "https://github.com/login/device/code",
        data={"client_id": client_id, "scope": "repo"},
        headers={"Accept": "application/json"},
    ).json()

    if "error" in verification_resp:
        if verification_resp["error"] == "Not found":
            raise ValueError("Invalid client id specified")
        else:
            raise ValueError(f"Got error response from GitHub: {verification_resp}")

    url = verification_resp["verification_uri"]
    code = verification_resp["user_code"]

    if in_jupyter:
        from IPython.display import Javascript, display

        display(Javascript(f'navigator.clipboard.writeText("{code}");'))
        print(f"The code {code} has been copied to your clipboard.")
        print(f"You have 15 minutes to go to {url} and paste it there.\n")
        ans = input(
            "Hit ENTER to open that page in a new tab (type anything to cancel)>"
        )
        if ans:
            print("Automatic opening canceled!")
        else:
            display(Javascript(f'window.open("{url}", "_blank");'))
    else:
        print(f"You have 15 minutes to go to {url} and enter the code: {code}")

    print("Waiting...", end="", flush=True)

    while True:
        time.sleep(verification_resp["interval"])
        print(".", end="", flush=True)
        access_resp = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": client_id,
                "device_code": verification_resp["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            headers={"Accept": "application/json"},
        ).json()
        if "access_token" in access_resp:
            print()
            return access_resp["access_token"], access_resp["expires_in"]


def main(args=None, in_jupyter=False):
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--client-id",
        default=os.environ.get("GH_SCOPED_CREDS_CLIENT_ID"),
        help="""
        Client ID of the GitHub app to authenticate with as the user
        """.strip(),
    )
    argparser.add_argument(
        "--git-credentials-path",
        default="/tmp/gh-scoped-creds",
        help="""
        Path to write the git-credentials file to. Current contents will be overwritten!
        """.strip(),
    )

    args = argparser.parse_args(args)

    if not args.client_id:
        print(
            "--client-id must be specified or GH_SCOPED_CREDS_CLIENT_ID environment variable must be set",
            file=sys.stderr,
        )
        sys.exit(1)

    access_token, expires_in = do_authenticate_device_flow(args.client_id, in_jupyter)

    # Create the file with appropriate permissions (0600) so other users can't read it
    with open(
        os.open(args.git_credentials_path, os.O_WRONLY | os.O_CREAT, 0o600), "w"
    ) as f:
        f.write(f"https://x-access-token:{access_token}@github.com\n")

    expires_in_hours = expires_in / 60 / 60
    success = (
        f"Success! Authentication will expire in {expires_in_hours:0.1f} hours.\n"
        f"Process completed on: {time.asctime()}."
    )
    if in_jupyter:
        from IPython.display import HTML, display

        success_html = success.replace("\n", "<br />")
        display(HTML(f'<p style="background-color:lightgreen;">{success_html}</p>'))
    else:
        print(success)


try:
    # Register an IPython magic if IPython is installed and we're running inside an IPython shell
    from IPython.core.magic import register_line_magic

    try:
        get_ipython()
        in_jupyter = True
    except NameError:
        # Not in ipython / jupyter, so we can't actually register this magic
        in_jupyter = False
    import shlex

    if in_jupyter:

        @register_line_magic
        def ghscopedcreds(line):
            """
            IPython magic for authenticating to GitHub
            """
            # Parse the passed in line into arguments using shell parsing logic
            args = shlex.split(line)
            main(args=args, in_jupyter=True)

except ImportError:
    pass
