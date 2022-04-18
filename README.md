# gh-scoped-creds

Provide finely scoped push access to GitHub from a JupyterHub or
HPC system.

## Goals

1. Allow users on a JupyterHub to grant push access to only *specific
   repositories* rather than *all* the repositories they have access to.
2. Do not store long-term credentials (like personal access tokens or
   ssh-keys) on disk, as they may get archived / fall into the wrong
   hands in the future.
3. Allow GitHub organization admins visibility and control over what
   repos users can push to from remote systems (like JupyterHub or a
   shared cluster), where other admins of the remote system might
   be able to access the files of users with push access to repos. This
   has serious implications for supply chain security, as credentials
   might be stolen or lost and serious vulnerabilities be pushed to
   the repo.

These goals are accomplished by:

1. Creating a [GitHub app](https://docs.github.com/en/developers/apps)
   specific to the remote service (JupyterHub, HPC cluster, etc). Users
   and GitHub organization admins can then provide fine grained, repo
   level access to this GitHub app - Users can only push to repos that have the
   app installed.
2. A commandline tool (`gh-scoped-creds`) that lets specific users
   authorize push access to the selected repositories temporarily - a token
   that expires after 8 hours.
3. An IPython Magic (`%ghscopedcreds`) that provides a convenient wrapper to call
   `gh-scoped-creds` from inside a Jupyter Notebook.

In the future, an optional web app might also be provided to aid in
authentication.

## Installation

You can install `gh-scoped-creds` from PyPI.

```bash
pip install gh-scoped-creds
```

## GitHub App configuration

1. Create a [GitHub app](https://docs.github.com/en/developers/apps) for
   use by the service (JupyterHub, HPC cluster, etc). You can either create
   it under your [personal account](https://github.com/settings/apps/new),
   or preferably under a GitHub organization account (Go to Settings ->
   Developer Settings -> GitHub Apps -> New GitHub app from the organization's
   GitHub page).

2. Give it a descriptive name and description, as your users will see this
   when they authenticate. Provide a link to a descriptive page explaining your
   service (if you are using a JupyterHub, this could be just your JupyterHub URL).

3. Select 'Enable Device Flow', as we rely on the [device flow](https://docs.github.com/en/enterprise-server@3.3/developers/apps/building-oauth-apps/authorizing-oauth-apps#device-flow)
   authentication method.

4. Disable webhooks (uncheck the 'Active' checkbox under 'Webhooks'). All other
   textboxes can be left empty.

5. Under 'Repository permissions', select 'Read & write' for 'Contents'. This
   will provide users authenticating via the app just enough permissions to push
   and pull from repositories.

6. Under 'Where can this GitHub App be installed?', select 'Any account'. This will
   enable users to push to their own user repositories or other organization repositaries,
   rather than just the repos of the user or organization owning this GitHub app.

7. Save the `Client ID` provided in the information page of the app. You'll need this
   in the client. Save the `Public link` as well, as users will need to use this to grant
   access to particular repositories.

## Client configuration

1. `gh-scoped-creds` will need to know the "Client ID" of the created GitHub app to
    perform authentication. This can be either set with the environment variable
	`GH_SCOPED_CREDS_CLIENT_ID`, or be passed in as a commandline parameter `--client-id` to
	the `gh-scoped-creds` script when users use it to authenticate.

1. `gh-scoped-creds` uses [`git-credentials-store`](https://git-scm.com/docs/git-credential-store)
   to provide appropriate authentication, by writing to a `/tmp/gh-scoped-creds`
   file. This makes sure we don't override the default `~/.git-credentials` file
   someone might be using. `git` will be automatically configured (via an entry
   in `~/.gitconfig`) to use this file for github.com credentials.  the new
   file.

   **Note for non-container uses**: If your users are on a HPC system or similar,
   where `/tmp` is not isolated for each user, you must set the file path to be
   under `$HOME`. The `gh-scoped-creds` commandline tool used by end users
   (documented below) accepts a `--git-credentials-path` that can be explicitly
   set.

## Usage

### Grant access to the GitHub app

Users will first need to go to the public page of the GitHub app, and
'Install' the app on their account and in organizations with repos they
want to push to. We *highly* recommend allowing access only to selected
repositories, and explicitly select the repositories this hosted service
(JupyterHub, HPC cluster, etc) should be able to push to. You can modify
this list afterwards, to make sure you only grant the required permissions.

Given the common usage pattern where you are only pushing to a limited
set of repositories from a particular hosted service, this should hopefully
not be too cumborsome.

### Authenticate to GitHub

The hosted service must have `gh-scoped-creds` installed.

1. Open a terminal, and type `gh-scoped-creds`. If you're in a Python based
   Jupyter Notebook, you can also do:

   ```python
   import gh_scoped_creds

   %ghscopedauth
   ```

   This will offer to open the page in a new window for you, and conveniently
   copy the code you need to paste in the new window too.

   If you're on a non-containerized system (like a HPC), you must
   also specify the path to put the credentials files in explicitly
   with `--git-credentials-path`. The same path must be used in the
   `gitconfig` configuration mentioned earlier.

2. It should give you a link to go to, and a code to input into the web page
   when that link is opened. Open the link, enter the code there (the page accepts
   pasting, so you can copy it from the output).

3. Grant access to the device in the web page, and you're done!

Authentication is valid for **8 hours**, and once it expires, this
process will need to be repeated. In the future, we might have a
web app or other process to make this less painful. However, keeping
the length of this session limited drastically helps with security too.

## Alternatives

1. Create an ssh key specifically for the hosted service (JupyterHub, HPC cluster, etc)
   and add it to your GitHub account. If the key doesn't have a passphrase, this is
   very insecure - anyone who can exfiltrate your key once can keep it and use it
   whenever they wish. Even with a passphrase, the key can still be exfiltrated and
   passphrase stolen when used. There's also no way to restrict which repositories
   this can push to, which is a big issue.

2. Create a [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
   and use that. This is a little *more* insecure than the ssh key, as it can be used
   to make requests on your behalf too after being stolen! There is also no way to
   restrict which repositories you can push to.

3. Create a [GitHub deploy key](https://docs.github.com/en/developers/overview/managing-deploy-keys)
   for each repository you want to push to, for each hosted service you want to push
   from. While this lets you control which repos this ssh key can access, it is still
   stored long term at risk and can be exfiltrated.