import argparse
import requests
import sys
import time
import os


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

    url  = verification_resp["verification_uri"]
    code = verification_resp["user_code"]

    if in_jupyter:
        from IPython.display import display, Javascript

        display(Javascript(f'navigator.clipboard.writeText("{code}");'))
        print(f'The code {code} has been copied to your clipboard.')
        print(f'You have 15 minutes to go to {url} and paste it there.\n')
        ans = input("Hit ENTER to open that page in a new tab (type anything to cancel)>")
        if ans:
            print("Automatic opening canceled!")
        else:
            display(Javascript(f'window.open("{url}", "_blank");'))
    else:
        print(f'You have 15 minutes to go to {url} and enter the code: {code}')

    print('Waiting...', end='', flush=True)

    while True:
        time.sleep(verification_resp["interval"])
        print('.', end='', flush=True)
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


def main(in_jupyter=False):
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--client-id",
        default=os.environ.get("GITHUB_APP_CLIENT_ID"),
        help="""
        Client ID of the GitHub app to authenticate with as the user
        """.strip(),
    )
    argparser.add_argument(
        "--git-credentials-path",
        default="/tmp/github-app-git-credentials",
        help="""
        Path to write the git-credentials file to. Current contents will be overwritten!
        """.strip(),
    )

    args = argparser.parse_args()

    if not args.client_id:
        print(
            "--client-id must be specified or GITHUB_APP_CLIENT_ID environment variable must be set",
            file=sys.stderr,
        )
        sys.exit(1)

    access_token, expires_in = do_authenticate_device_flow(args.client_id, in_jupyter)
    expires_in_hours = expires_in / 60 / 60
    success = (f"Success! Authentication will expire in {expires_in_hours:0.1f} hours.\n<br>"
               f"Process completed on: {time.asctime()}.")
    if in_jupyter:
        from IPython.display import display, HTML
        display(HTML(f'<p style="background-color:lightgreen;">{success}</p>'))
    else:
        print(success)

    # Create the file with appropriate permissions (0600) so other users can't read it
    with open(os.open(args.git_credentials_path, os.O_WRONLY | os.O_CREAT, 0o600), "w") as f:
        f.write(f"https://x-access-token:{access_token}@github.com\n")
