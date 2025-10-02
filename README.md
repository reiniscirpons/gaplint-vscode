# gaplint for vscode

A VSCode extension wrapper around
[`gaplint`](https://github.com/james-d-mitchell/gaplint) for highlighting linting errors in
[`gap`](https://www.gap-system.org/) code.

Supports both `gap` and `gaptst` files. For more information about `gaplint`, see
[james-d-mitchell/gaplint](https://github.com/james-d-mitchell/gaplint).

## Troubleshooting and FAQ

Please try updating to the latest version of `gaplint-vscode` to fix any
potential issues. Here are some common issues and fixes that may be encountered:

> **1. The version `v0.1.0` language server crashes repeatedly with a Python
> runtime error.**

There was a bug in `gaplint-vscode` version `v0.1.0` that causes this.
Upgrading to `v0.1.1` should fix this.

> **2. No error highlighting after updating to latest version, plugin complains
> that it can't find a `gaplint` executable.**

Try resetting the `Gaplint: Path` configuration option in VSCode and set the
`Gaplint: Import Strategy` option to `useBundled`. The `gaplint-vscode` plugin
changed the way `gaplint` was sourced between version `v0.0.2` and `v0.1.0` of
`gaplint-vscode` which could cause this error.

Alternatively, if the above does not resolve your issue, or if you would like
to use your own local installation of `gaplint`, install or upgrade `gaplint`
locally via `pip`, e.g.

```bash
python3 -m pip install --upgrade gaplint
```

and set the `Gaplint: Path` configuration option to the full path containing
`gaplint`. This path can be found by running `which gaplint` in your terminal
on Linux. See
[james-d-mitchell/gaplint](https://github.com/james-d-mitchell/gaplint) for
more information on installing gaplint.

Note that setting the `Gaplint: Path` option may break the plugin in subsequent
updates.

> **3. The plugin only highlights whole lines, is there a way to make it
> highlight the error more specifically?**

Yes, this feature was added in `v0.1.0`, please try updating the plugin. Doing
so may cause new issues, see the prior troubleshooting steps for some help.

If using a local install of `gaplint` via the `Gaplint: Path` configuration
option of `gaplint-vscode`, make sure that the local install of `gaplint`
supports the `--ranges` option by running `gaplint --ranges` in your terminal.
If it does not, then upgrade the local install of `gaplint` (see above),
the `--ranges` option was introduced in `v1.5.0` of `gaplint`.

If the problem persists, try manually adding the `--ranges` option to the
`Gaplint: Args` configuration option.

> **4. A warning pops up telling me my gaplint version is unsupported!**

Update to the latest version of `gaplint-vscode` and follow the steps in
the troubleshooting item 2. See also item 3. above if you would like
better warning highlighting.

The warning may persist in rare cases due to difficulties in detecting the
`gaplint` version, if so please open an issue on the `gaplint-vscode` issue
tracker (below).

> **5. My issue is not listed above or none of the prior troubleshooting
> fixed my issue.**

Please file an issue in the `gaplint-vscode` issue tracker on github:

> [https://github.com/reiniscirpons/gaplint-vscode/issues](https://github.com/reiniscirpons/gaplint-vscode/issues)
