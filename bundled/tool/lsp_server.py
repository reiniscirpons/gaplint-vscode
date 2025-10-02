# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Implementation of tool support over LSP."""
from __future__ import annotations

import copy
import json
import os
import pathlib
import re
import sys
import sysconfig
import traceback
from typing import Any, Dict, List, Optional, Sequence, Tuple


# **********************************************************
# Update sys.path before importing any bundled libraries.
# **********************************************************
def update_sys_path(path_to_add: str, strategy: str) -> None:
    """Add given path to `sys.path`."""
    if path_to_add not in sys.path and os.path.isdir(path_to_add):
        if strategy == "useBundled":
            sys.path.insert(0, path_to_add)
        else:
            sys.path.append(path_to_add)


# **********************************************************
# Update PATH before running anything.
# **********************************************************
def update_environ_path() -> None:
    """Update PATH environment variable with the 'scripts' directory.
    Windows: .venv/Scripts
    Linux/MacOS: .venv/bin
    """
    scripts = sysconfig.get_path("scripts")
    paths_variants = ["Path", "PATH"]

    for var_name in paths_variants:
        if var_name in os.environ:
            paths = os.environ[var_name].split(os.pathsep)
            if scripts not in paths:
                paths.insert(0, scripts)
                os.environ[var_name] = os.pathsep.join(paths)
                break


# Ensure that we can import LSP libraries, and other bundled libraries.
BUNDLE_DIR = pathlib.Path(__file__).parent.parent
# Always use bundled server files.
update_sys_path(os.fspath(BUNDLE_DIR / "tool"), "useBundled")
update_sys_path(
    os.fspath(BUNDLE_DIR / "libs"),
    os.getenv("LS_IMPORT_STRATEGY", "useBundled"),
)
update_environ_path()

# **********************************************************
# Imports needed for the language server goes below this.
# **********************************************************
# pylint: disable=wrong-import-position,import-error
import lsp_jsonrpc as jsonrpc
import lsp_utils as utils
from lsprotocol import types as lsp
from pygls import server, uris, workspace

WORKSPACE_SETTINGS = {}
GLOBAL_SETTINGS = {}
# TODO(reiniscirpons): should this be "runner.py" or "lsp_runner.py"?
# Seems like a difference between vscode-pylint and
# vscode-python-tools-extension-template
RUNNER = pathlib.Path(__file__).parent / "runner.py"

MAX_WORKERS = 5
LSP_SERVER = server.LanguageServer(
    name="gaplint-server", version="0.1.1", max_workers=MAX_WORKERS
)


# **********************************************************
# Tool specific code goes below this.
# **********************************************************

# Reference:
#  LS Protocol:
#  https://microsoft.github.io/language-server-protocol/specifications/specification-3-16/
#
#  Sample implementations:
#  Pylint: https://github.com/microsoft/vscode-pylint/blob/main/bundled/tool
#  Black: https://github.com/microsoft/vscode-black-formatter/blob/main/bundled/tool
#  isort: https://github.com/microsoft/vscode-isort/blob/main/bundled/tool

TOOL_MODULE = "gaplint"
TOOL_DISPLAY = "gaplint"
DOCUMENTATION_HOME = "https://github.com/james-d-mitchell/gaplint"

# Default arguments always passed to gaplint.
TOOL_ARGS = []  # default arguments always passed to your tool.

# Minimum version of gaplint supported.
# TODO (reiniscirpons): Check what the actual oldest supported version is
MIN_VERSION = "1.4.0"


# **********************************************************
# Linting features start here
# **********************************************************

#  See `pylint` implementation for a full featured linter extension:
#  Pylint: https://github.com/microsoft/vscode-pylint/blob/main/bundled/tool

# Captures version of `gaplint` in various workspaces.
VERSION_TABLE: Dict[str, Tuple[int, int, int]] = {}


@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(params: lsp.DidOpenTextDocumentParams) -> None:
    """LSP handler for textDocument/didOpen request."""
    document = LSP_SERVER.workspace.get_text_document(params.text_document.uri)
    diagnostics: list[lsp.Diagnostic] = _linting_helper(document)
    LSP_SERVER.publish_diagnostics(document.uri, diagnostics)


@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(params: lsp.DidSaveTextDocumentParams) -> None:
    """LSP handler for textDocument/didSave request."""
    document = LSP_SERVER.workspace.get_text_document(params.text_document.uri)
    diagnostics: list[lsp.Diagnostic] = _linting_helper(document)
    LSP_SERVER.publish_diagnostics(document.uri, diagnostics)


@LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
def did_close(params: lsp.DidCloseTextDocumentParams) -> None:
    """LSP handler for textDocument/didClose request."""
    document = LSP_SERVER.workspace.get_text_document(params.text_document.uri)
    # Publishing empty diagnostics to clear the entries for this file.
    LSP_SERVER.publish_diagnostics(document.uri, [])


# TODO(reiniscirpons): Implement this once gaplint is a bit more performant
if os.getenv("VSCODE_GAPLINT_LINT_ON_CHANGE"):

    # @LSP_SERVER.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
    # def did_change(params: lsp.DidChangeTextDocumentParams) -> None:
    #     """LSP handler for textDocument/didChange request."""
    #     document = LSP_SERVER.workspace.get_text_document(params.text_document.uri)
    #     diagnostics: list[lsp.Diagnostic] = _linting_helper(document)
    #     LSP_SERVER.publish_diagnostics(document.uri, diagnostics)
    pass


def _linting_helper(document: workspace.Document) -> List[lsp.Diagnostic]:
    try:
        extra_args = []

        code_workspace = _get_settings_by_document(document)["workspaceFS"]
        if VERSION_TABLE.get(code_workspace, None):
            major, minor, _ = VERSION_TABLE[code_workspace]
            LSP_SERVER.show_message_log(
                f"Detected gaplint version: {major}.{minor}",
                lsp.MessageType.Info,
            )
            if (major, minor) >= (1, 5):
                extra_args += ["--ranges"]

        # TODO: (reiniscirpons) Once gaplint supports stdin, change use_stdin to True
        result = _run_tool_on_document(document, use_stdin=False, extra_args=extra_args)
        if result is None or result.stderr is None:
            return []
        log_to_output(f"{document.uri} :\r\n{result.stderr}")

        # deep copy here to prevent accidentally updating global settings.
        settings = copy.deepcopy(_get_settings_by_document(document))
        return _parse_output(result.stderr, severity=settings["severity"])
    except Exception:  # pylint: disable=broad-except
        LSP_SERVER.show_message_log(
            f"Linting failed with error:\r\n{traceback.format_exc()}",
            lsp.MessageType.Error,
        )
    return []


def _get_severity(
    symbol: str, code: str, code_type: str, severity: Dict[str, str]
) -> lsp.DiagnosticSeverity:
    """Converts severity provided by linter to LSP specific value."""
    symbol_to_severity = {"M": "error", "W": "warning"}
    value = (
        severity.get(code, None)
        or severity.get(code_type, None)
        or severity.get(symbol, None)
        or severity.get(symbol_to_severity.get(symbol, None), "Warning")
    )
    try:
        return lsp.DiagnosticSeverity[value]
    except KeyError:
        pass

    return lsp.DiagnosticSeverity.Warning


DIAGNOSTIC_REGEXES = [
    re.compile(regex)
    for regex in (
        r".*:(?P<line>\d+)-(?P<endLine>\d+):(?P<column>\d+)-(?P<endColumn>\d+): (?P<message>[^\[\r\n]*) \[(?P<code>(?P<symbol>\w)\d+)/(?P<code_type>[^\]\r\n]*)\]",  # pylint: disable=line-too-long
        r".*:(?P<line>\d+):(?P<column>\d+)-(?P<endColumn>\d+): (?P<message>[^\[\r\n]*) \[(?P<code>(?P<symbol>\w)\d+)/(?P<code_type>[^\]\r\n]*)\]",  # pylint: disable=line-too-long
        r".*:(?P<line>\d+):(?P<column>\d+): (?P<message>[^\[\r\n]*) \[(?P<code>(?P<symbol>\w)\d+)/(?P<code_type>[^\]\r\n]*)\]",  # pylint: disable=line-too-long
        r".*:(?P<line>\d+)-(?P<endLine>\d+): (?P<message>[^\[\r\n]*) \[(?P<code>(?P<symbol>\w)\d+)/(?P<code_type>[^\]\r\n]*)\]",  # pylint: disable=line-too-long
        r".*:(?P<line>\d+): (?P<message>[^\[\r\n]*) \[(?P<code>(?P<symbol>\w)\d+)/(?P<code_type>[^\]\r\n]*)\]",  # pylint: disable=line-too-long
    )
]


# pylint: disable=too-many-locals
def _parse_output(
    content: str,
    severity: Dict[str, str],
) -> List[lsp.Diagnostic]:
    """Parses linter messages and return LSP diagnostic object for each message."""
    raw_lines: list[str] = content.splitlines()
    diagnostics = []

    line_offset = 1
    column_offset = 1

    for raw_line in raw_lines:
        if raw_line.startswith("'") and raw_line.endswith("'"):
            raw_line = raw_line[1:-1]

        match = None
        for regex in DIAGNOSTIC_REGEXES:
            match = regex.match(raw_line)
            if match is not None:
                break
        else:
            continue

        data = match.groupdict()

        line = max(int(data.get("line", line_offset)) - line_offset, 0)
        column = max(int(data.get("column", column_offset)) - column_offset, 0)
        start_position = lsp.Position(
            line=line,
            character=column,
        )

        end_line = data.get("endLine")
        end_line = max(int(end_line) - line_offset, 0) if end_line is not None else line
        end_column = data.get("endColumn")
        end_column = (
            max(int(end_column) - column_offset, 0)
            if end_column is not None
            # NOTE(reiniscirpons): This may not be the correct behavior if
            # end_column is None. We may want to be contextual depending on
            # whether column was None as well.
            else (len(raw_line) - column_offset)
        )
        end_position = lsp.Position(
            line=end_line,
            character=end_column,
        )

        code = data["code"]
        code_type = data["code_type"]
        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=start_position,
                end=end_position,
            ),
            message=data["message"],
            severity=_get_severity(
                data["symbol"], data["code"], data["code_type"], severity
            ),
            code=f"{code}/{code_type}",
            source=TOOL_DISPLAY,
        )
        diagnostics.append(diagnostic)

    return diagnostics


# **********************************************************
# Linting features end here
# **********************************************************

# TODO(reiniscirpons): Maybe add code actions for quickly fixing some errors
# e.g. missing spaces.


# **********************************************************
# Required Language Server Initialization and Exit handlers.
# **********************************************************
@LSP_SERVER.feature(lsp.INITIALIZE)
def initialize(params: lsp.InitializeParams) -> None:
    """LSP handler for initialize request."""
    log_to_output(f"CWD Server: {os.getcwd()}")
    import_strategy = os.getenv("LS_IMPORT_STRATEGY", "useBundled")
    update_sys_path(os.getcwd(), import_strategy)

    GLOBAL_SETTINGS.update(**params.initialization_options.get("globalSettings", {}))

    settings = params.initialization_options["settings"]
    _update_workspace_settings(settings)
    log_to_output(
        f"Settings used to run Server:\r\n{json.dumps(settings, indent=4, ensure_ascii=False)}\r\n"
    )
    log_to_output(
        f"Global settings:\r\n{json.dumps(GLOBAL_SETTINGS, indent=4, ensure_ascii=False)}\r\n"
    )

    # Add extra paths to sys.path
    setting = _get_settings_by_path(pathlib.Path(os.getcwd()))
    for extra in setting.get("extraPaths", []):
        update_sys_path(extra, import_strategy)

    paths = "\r\n   ".join(sys.path)
    log_to_output(f"sys.path used to run Server:\r\n   {paths}")

    _log_version_info()


@LSP_SERVER.feature(lsp.EXIT)
def on_exit(_params: Optional[Any] = None) -> None:
    """Handle clean up on exit."""
    jsonrpc.shutdown_json_rpc()


@LSP_SERVER.feature(lsp.SHUTDOWN)
def on_shutdown(_params: Optional[Any] = None) -> None:
    """Handle clean up on shutdown."""
    jsonrpc.shutdown_json_rpc()


def _log_version_info() -> None:
    for value in WORKSPACE_SETTINGS.values():
        try:
            # pylint: disable=import-outside-toplevel
            from packaging.version import InvalidVersion
            from packaging.version import parse as parse_version

            settings = copy.deepcopy(value)
            # NOTE(reiniscirpons): using the --version parameter is super
            # unhelpful at the moment, since it sometimes picks up random
            # versions in the env instead. This is the reason for the
            # supports ranges check further down.
            result = _run_tool(["--version"], settings)
            code_workspace = settings["workspaceFS"]
            log_to_output(
                f"Version info for linter running for {code_workspace}:\r\n"
                f"stdout: {result.stdout}\r\n"
                f"stderr: {result.stderr}"
            )

            # This is text we get from running `pylint --version`
            # gaplint version 1.6.1
            textual_version_info = result.stdout
            # Not sure whether its in stdin or stderr, so try both
            if textual_version_info is None or len(textual_version_info) == 0:
                textual_version_info = result.stderr

            first_line = textual_version_info.splitlines(keepends=False)[0]
            actual_version = first_line.split(" ")[2]

            try:
                version = parse_version(actual_version)
            except InvalidVersion:
                # Older versions of gaplint prior to 1.1.0 seem to not have the
                # --version option
                version = parse_version("1.0.0")

            # Check if we support ranges
            result_ranges = _run_tool(["--ranges"], settings)
            log_to_output(
                f"Ranges support info for linter running for {code_workspace}:\r\n"
                f"stdout: {result_ranges.stdout}\r\n"
                f"stderr: {result_ranges.stderr}"
            )
            # If dont support ranges, we expect to see something like:
            # usage: gaplint [options]
            # gaplint: error: unrecognized arguments: --ranges
            textual_ranges_info = result.stdout
            # Not sure whether its in stdin or stderr, so try both
            if textual_ranges_info is None or len(textual_ranges_info) == 0:
                textual_ranges_info = result.stderr

            supports_ranges = True
            if "--ranges" in textual_ranges_info:
                supports_ranges = False

            if version < parse_version("1.5.0") and supports_ranges:
                log_to_output(
                    f"WARNING, detected version {TOOL_MODULE}=={actual_version}, "
                    f"but tool supports ranges (available from 1.5.0)\r\n"
                    f"Automatically bumping detected version to 1.5.0"
                )
                version = parse_version("1.5.0")

            min_version = parse_version(MIN_VERSION)
            VERSION_TABLE[code_workspace] = (
                version.major,
                version.minor,
                version.micro,
            )

            if version < min_version:
                log_error(
                    f"Version of linter running for {code_workspace} is NOT supported:\r\n"
                    f"SUPPORTED {TOOL_MODULE}>={min_version}\r\n"
                    f"FOUND {TOOL_MODULE}=={actual_version}\r\n"
                )
            else:
                log_to_output(
                    f"SUPPORTED {TOOL_MODULE}>={min_version}\r\n"
                    f"FOUND {TOOL_MODULE}=={actual_version}\r\n"
                )
        except:  # pylint: disable=bare-except
            log_to_output(
                f"Error while detecting gaplint version:\r\n{traceback.format_exc()}"
            )


# *****************************************************
# Internal functional and settings management APIs.
# *****************************************************
def _get_global_defaults():
    return {
        "enabled": GLOBAL_SETTINGS.get("enabled", True),
        "path": GLOBAL_SETTINGS.get("path", []),
        "interpreter": GLOBAL_SETTINGS.get("interpreter", [sys.executable]),
        "args": GLOBAL_SETTINGS.get("args", []),
        "severity": GLOBAL_SETTINGS.get(
            "severity",
            {
                "error": "Error",
                "warning": "Warning",
            },
        ),
        "ignorePatterns": [],
        "importStrategy": GLOBAL_SETTINGS.get("importStrategy", "useBundled"),
        "showNotifications": GLOBAL_SETTINGS.get("showNotifications", "off"),
        "extraPaths": GLOBAL_SETTINGS.get("extraPaths", []),
    }


def _update_workspace_settings(settings):
    if not settings:
        key = utils.normalize_path(os.getcwd())
        WORKSPACE_SETTINGS[key] = {
            "cwd": key,
            "workspaceFS": key,
            "workspace": uris.from_fs_path(key),
            **_get_global_defaults(),
        }
        return

    for setting in settings:
        key = utils.normalize_path(uris.to_fs_path(setting["workspace"]))
        WORKSPACE_SETTINGS[key] = {
            **setting,
            "workspaceFS": key,
        }


def _get_settings_by_path(file_path: pathlib.Path):
    workspaces = {s["workspaceFS"] for s in WORKSPACE_SETTINGS.values()}

    while file_path != file_path.parent:
        str_file_path = utils.normalize_path(file_path)
        if str_file_path in workspaces:
            return WORKSPACE_SETTINGS[str_file_path]
        file_path = file_path.parent

    setting_values = list(WORKSPACE_SETTINGS.values())
    return setting_values[0]


def _get_document_key(document: workspace.Document):
    if WORKSPACE_SETTINGS:
        document_workspace = pathlib.Path(document.path)
        workspaces = {s["workspaceFS"] for s in WORKSPACE_SETTINGS.values()}

        # Find workspace settings for the given file.
        while document_workspace != document_workspace.parent:
            norm_path = utils.normalize_path(document_workspace)
            if norm_path in workspaces:
                return norm_path
            document_workspace = document_workspace.parent

    return None


def _get_settings_by_document(document: workspace.Document | None):
    if document is None or document.path is None:
        return list(WORKSPACE_SETTINGS.values())[0]

    key = _get_document_key(document)
    if key is None:
        # This is either a non-workspace file or there is no workspace.
        key = utils.normalize_path(pathlib.Path(document.path).parent)
        return {
            "cwd": key,
            "workspaceFS": key,
            "workspace": uris.from_fs_path(key),
            **_get_global_defaults(),
        }

    return WORKSPACE_SETTINGS[str(key)]


# *****************************************************
# Internal execution APIs.
# *****************************************************
def get_cwd(settings: Dict[str, Any], document: Optional[workspace.Document]) -> str:
    """Returns cwd for the given settings and document."""
    if settings["cwd"] == "${workspaceFolder}":
        return settings["workspaceFS"]

    if settings["cwd"] == "${fileDirname}":
        if document is not None:
            return os.fspath(pathlib.Path(document.path).parent)
        return settings["workspaceFS"]

    return settings["cwd"]


# pylint: disable=too-many-branches,too-many-statements
def _run_tool_on_document(
    document: workspace.Document,
    use_stdin: bool = False,
    extra_args: Optional[Sequence[str]] = None,
) -> utils.RunResult | None:
    """Runs tool on the given document.

    if use_stdin is true then contents of the document is passed to the
    tool via stdin.
    """
    if extra_args is None:
        extra_args = []

    # deep copy here to prevent accidentally updating global settings.
    settings = copy.deepcopy(_get_settings_by_document(document))

    if not settings["enabled"]:
        log_warning(f"Skipping file [Linting Disabled]: {document.path}")
        log_warning("See `gaplint.enabled` in settings.json to enabling linting.")
        return None

    if str(document.uri).startswith("vscode-notebook-cell"):
        log_warning(f"Skipping notebook cells [Not Supported]: {str(document.uri)}")
        return None

    if utils.is_stdlib_file(document.path):
        log_warning(
            f"Skipping standard library file (stdlib excluded): {document.path}"
        )

        return None

    if utils.is_match(settings["ignorePatterns"], document.path):
        log_warning(
            f"Skipping file due to `gaplint.ignorePatterns` match: {document.path}"
        )
        return None

    code_workspace = settings["workspaceFS"]
    cwd = get_cwd(settings, document)

    use_path = False
    use_rpc = False
    if settings["path"]:
        # 'path' setting takes priority over everything.
        use_path = True
        argv = settings["path"]
    elif settings["interpreter"] and not utils.is_current_interpreter(
        settings["interpreter"][0]
    ):
        # If there is a different interpreter set use JSON-RPC to the subprocess
        # running under that interpreter.
        argv = [TOOL_MODULE]
        use_rpc = True
    else:
        # if the interpreter is same as the interpreter running this
        # process then run as module.
        argv = [TOOL_MODULE]

    argv += TOOL_ARGS + settings["args"] + extra_args

    # pygls normalizes the path to lowercase on windows, but we need to resolve the
    # correct capitalization to avoid https://github.com/pylint-dev/pylint/issues/10137
    resolved_path = str(pathlib.Path(document.path).resolve())

    if use_stdin:
        # TODO(reiniscirpons): Change this once we support stdin
        argv += [resolved_path]
        # argv += ["--from-stdin", resolved_path]
    else:
        argv += [resolved_path]

    env = None
    if use_path or use_rpc:
        # for path and rpc modes we need to set PYTHONPATH, for module or API mode
        # we would have already set the extra paths in the initialize handler.
        env = _get_updated_env(settings)

    if use_path:
        # This mode is used when running executables.
        log_to_output(" ".join(argv))
        log_to_output(f"CWD Server: {cwd}")
        result = utils.run_path(
            argv=argv,
            use_stdin=use_stdin,
            cwd=cwd,
            source=document.source.replace("\r\n", "\n"),
            env=env,
        )
        if result.stderr:
            log_to_output(result.stderr)
    elif use_rpc:
        # This mode is used if the interpreter running this server is different from
        # the interpreter used for running this server.
        log_to_output(" ".join(settings["interpreter"] + ["-m"] + argv))
        log_to_output(f"CWD Linter: {cwd}")

        result = jsonrpc.run_over_json_rpc(
            workspace=code_workspace,
            interpreter=settings["interpreter"],
            module=TOOL_MODULE,
            argv=argv,
            use_stdin=use_stdin,
            cwd=cwd,
            source=document.source,
            env=env,
        )
        result = _to_run_result_with_logging(result)
    else:
        # In this mode the tool is run as a module in the same process as the language server.
        log_to_output(" ".join([sys.executable, "-m"] + argv))
        log_to_output(f"CWD Linter: {cwd}")
        # This is needed to preserve sys.path, in cases where the tool modifies
        # sys.path and that might not work for this scenario next time around.
        with utils.substitute_attr(sys, "path", [""] + sys.path[:]):
            try:
                result = utils.run_module(
                    module=TOOL_MODULE,
                    argv=argv,
                    use_stdin=use_stdin,
                    cwd=cwd,
                    source=document.source,
                )
            except Exception:
                log_error(traceback.format_exc(chain=True))
                raise
        if result.stderr:
            log_to_output(result.stderr)

    return result


def _run_tool(extra_args: Sequence[str], settings: Dict[str, Any]) -> utils.RunResult:
    """Runs tool."""
    code_workspace = settings["workspaceFS"]
    cwd = get_cwd(settings, None)

    use_path = False
    use_rpc = False
    if len(settings["path"]) > 0:
        # 'path' setting takes priority over everything.
        use_path = True
        argv = settings["path"]
    elif len(settings["interpreter"]) > 0 and not utils.is_current_interpreter(
        settings["interpreter"][0]
    ):
        # If there is a different interpreter set use JSON-RPC to the subprocess
        # running under that interpreter.
        argv = [TOOL_MODULE]
        use_rpc = True
    else:
        # if the interpreter is same as the interpreter running this
        # process then run as module.
        argv = [TOOL_MODULE]

    argv += extra_args

    env = None
    if use_path or use_rpc:
        # for path and rpc modes we need to set PYTHONPATH, for module or API mode
        # we would have already set the extra paths in the initialize handler.
        env = _get_updated_env(settings)

    if use_path:
        # This mode is used when running executables.
        log_to_output(" ".join(argv))
        log_to_output(f"CWD Server: {cwd}")
        result = utils.run_path(argv=argv, use_stdin=True, cwd=cwd, env=env)
        if result.stderr:
            log_to_output(result.stderr)
    elif use_rpc:
        # This mode is used if the interpreter running this server is different from
        # the interpreter used for running this server.
        log_to_output(" ".join(settings["interpreter"] + ["-m"] + argv))
        log_to_output(f"CWD Linter: {cwd}")
        result = jsonrpc.run_over_json_rpc(
            workspace=code_workspace,
            interpreter=settings["interpreter"],
            module=TOOL_MODULE,
            argv=argv,
            use_stdin=True,
            cwd=cwd,
            env=env,
        )
        result = _to_run_result_with_logging(result)
    else:
        # In this mode the tool is run as a module in the same process as the language server.
        log_to_output(" ".join([sys.executable, "-m"] + argv))
        log_to_output(f"CWD Linter: {cwd}")
        # This is needed to preserve sys.path, in cases where the tool modifies
        # sys.path and that might not work for this scenario next time around.
        with utils.substitute_attr(sys, "path", [""] + sys.path[:]):
            try:
                result = utils.run_module(
                    module=TOOL_MODULE, argv=argv, use_stdin=True, cwd=cwd
                )
            except Exception:
                log_error(traceback.format_exc(chain=True))
                raise
        if result.stderr:
            log_to_output(result.stderr)

    log_to_output(f"\r\n{result.stdout}\r\n")
    return result


def _get_updated_env(settings: Dict[str, Any]) -> str:
    """Returns the updated environment variables."""
    extra_paths = settings.get("extraPaths", [])
    paths = os.environ.get("PYTHONPATH", "").split(os.pathsep) + extra_paths
    python_paths = os.pathsep.join([p for p in paths if len(p) > 0])

    env = {
        "LS_IMPORT_STRATEGY": settings["importStrategy"],
        "PYTHONUTF8": "1",
    }
    if python_paths:
        env["PYTHONPATH"] = python_paths
    return env


def _to_run_result_with_logging(rpc_result: jsonrpc.RpcRunResult) -> utils.RunResult:
    error = ""
    if rpc_result.exception:
        log_error(rpc_result.exception)
        error = rpc_result.exception
    elif rpc_result.stderr:
        log_to_output(rpc_result.stderr)
        error = rpc_result.stderr
    return utils.RunResult(rpc_result.stdout, error)


# *****************************************************
# Logging and notification.
# *****************************************************
def log_to_output(
    message: str, msg_type: lsp.MessageType = lsp.MessageType.Log
) -> None:
    """Logs messages to Output > gaplint channel only."""
    LSP_SERVER.show_message_log(message, msg_type)


def log_error(message: str) -> None:
    """Logs messages with notification on error."""
    LSP_SERVER.show_message_log(message, lsp.MessageType.Error)
    if os.getenv("LS_SHOW_NOTIFICATION", "off") in ["onError", "onWarning", "always"]:
        LSP_SERVER.show_message(message, lsp.MessageType.Error)


def log_warning(message: str) -> None:
    """Logs messages with notification on warning."""
    LSP_SERVER.show_message_log(message, lsp.MessageType.Warning)
    if os.getenv("LS_SHOW_NOTIFICATION", "off") in ["onWarning", "always"]:
        LSP_SERVER.show_message(message, lsp.MessageType.Warning)


def log_always(message: str) -> None:
    """Logs messages with notification."""
    LSP_SERVER.show_message_log(message, lsp.MessageType.Info)
    if os.getenv("LS_SHOW_NOTIFICATION", "off") in ["always"]:
        LSP_SERVER.show_message(message, lsp.MessageType.Info)


# *****************************************************
# Start the server.
# *****************************************************
if __name__ == "__main__":
    LSP_SERVER.start_io()
