# Change Log

### v0.1.1

- Fix a Python f-string error in `lsp_server.py` which caused runtime errors on
  more recent versions of Python runtime.
- Update README to include common troubleshooting steps.

### v0.1.0

- Bump `gaplint` to `1.6.1`.
- Add support for range highlighting, with fallback for older versions.
- Add new config options for overriding severity.
- Add warning message if detected `gaplint` version is too old.
- Fix bundling issue (`./bundled/libs` directory needs to be purged in between builds.).

### v0.0.2

- Add support for `gaptst` file linting.
- Bump `gaplint` to `1.4.0`.

### v0.0.1

- Initial release.
- Add support for linting `gap` files with `gaplint` version `1.3.2`.
