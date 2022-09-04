# How to make a release

`gh-scoped-creds` is a package [available on
PyPI](https://pypi.org/project/gh-scoped-creds/) and on conda-forge.

These are instructions on how to make a release on PyPI. The PyPI release is
done automatically by CI when a git tag is pushed. Following a PyPI release is
made, a pull request will be opened to the conda-forge feedstock.

For you to follow along according to these instructions, you need:

- To have push rights to the [gh-scoped-creds GitHub
  repository](https://github.com/jupyterhub/gh-scoped-creds).

## Steps to make a release

1. Make sure `CHANGELOG.md` is up-to-date ahead of time with a dedicated
   changelog PR. [github-activity][] can help with this.

1. Checkout main and make sure it is up to date.

   ```shell
   ORIGIN=${ORIGIN:-origin} # set to the canonical remote, e.g. 'upstream' if 'origin' is not the official repo
   git checkout main
   git fetch $ORIGIN main
   git reset --hard $ORIGIN/main
   # WARNING! This next command deletes any untracked files in the repo
   git clean -xfd
   ```

1. Set the `version` field in setup.py appropriately and make a commit.

   ```shell
   git add setup.py
   VERSION=...  # e.g. 1.2.3
   git commit -m "release $VERSION"
   git tag -a $VERSION -m $VERSION HEAD
   ```

1. Reset the version field in setup.py appropriately with an incremented patch
   version and a dev element, then make a commit.

   ```shell
   git add setup.py
   git commit -m "back to dev"
   ```

1. Verify your git history looks good.

   ```shell
   git log
   ```

1. Push the commits and git tags.

   ```
   git push --atomic --follow-tags $ORIGIN main
   ```

1. Verify that [the GitHub workflow](https://github.com/jupyterhub/gh-scoped-creds/actions?query=workflow%3ARelease)
   triggers and succeeds, and that that [the PyPI
   project](https://pypi.org/project/gh-scoped-creds) received a new release.

1. Following the release to PyPI, an automated PR should arrive to
   [conda-forge/gh-scoped-creds-feedstock][], check for the tests to succeed on
   this PR and then merge it to successfully update the package for `conda` on
   the conda-forge channel.

[github-activity]: https://github.com/executablebooks/github-activity
[conda-forge/gh-scoped-creds-feedstock]: https://github.com/conda-forge/gh-scoped-creds-feedstock
