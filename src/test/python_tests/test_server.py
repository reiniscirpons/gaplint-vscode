# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Test for linting over LSP.
"""

from threading import Event

from hamcrest import assert_that, is_

from .lsp_test_client import constants, defaults, session, utils

TEST_FILE_PATH = constants.TEST_DATA / "sample1" / "test1.g"
TEST_FILE_URI = utils.as_uri(str(TEST_FILE_PATH))
SERVER_INFO = utils.get_server_info_defaults()
TIMEOUT = 10  # 10 seconds


def test_linting_example():
    """Test to linting on file open."""
    contents = TEST_FILE_PATH.read_text()

    actual = []
    with session.LspSession() as ls_session:
        ls_session.initialize(defaults.VSCODE_DEFAULT_INITIALIZE)

        done = Event()

        def _handler(params):
            nonlocal actual
            actual = params
            done.set()

        ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

        ls_session.notify_did_open(
            {
                "textDocument": {
                    "uri": TEST_FILE_URI,
                    "languageId": "gap",
                    "version": 1,
                    "text": contents,
                }
            }
        )

        # wait for some time to receive all notifications
        done.wait(TIMEOUT)

        expected = {
            "uri": TEST_FILE_URI,
            "diagnostics": [
                {
                    "range": {
                        "start": {"line": 20, "character": 0},
                        "end": {"line": 20, "character": 147},
                    },
                    "message": "Unused function arguments: arg",
                    "severity": 2,
                    "code": "W046/unused-func-args",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 46, "character": 0},
                        "end": {"line": 46, "character": 139},
                    },
                    "message": "Unused local variables: t",
                    "severity": 2,
                    "code": "W000/analyse-lvars",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 50, "character": 0},
                        "end": {"line": 50, "character": 139},
                    },
                    "message": "Unused local variables: t",
                    "severity": 2,
                    "code": "W000/analyse-lvars",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 62, "character": 0},
                        "end": {"line": 62, "character": 145},
                    },
                    "message": "Unused function arguments: z",
                    "severity": 2,
                    "code": "W046/unused-func-args",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 65, "character": 0},
                        "end": {"line": 65, "character": 153},
                    },
                    "message": "Variables assigned but never used: test",
                    "severity": 2,
                    "code": "W000/analyse-lvars",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 29, "character": 0},
                        "end": {"line": 29, "character": 147},
                    },
                    "message": "Consecutive empty lines",
                    "severity": 2,
                    "code": "W001/consecutive-empty-lines",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 62, "character": 0},
                        "end": {"line": 62, "character": 151},
                    },
                    "message": "One line function could be a lambda",
                    "severity": 2,
                    "code": "W034/1-line-function",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 5, "character": 0},
                        "end": {"line": 5, "character": 163},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 5, "character": 0},
                        "end": {"line": 5, "character": 152},
                    },
                    "message": "Wrong whitespace around operator +",
                    "severity": 2,
                    "code": "W020/whitespace-op-plus",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 7, "character": 0},
                        "end": {"line": 7, "character": 162},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 7, "character": 0},
                        "end": {"line": 7, "character": 163},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 7, "character": 0},
                        "end": {"line": 7, "character": 142},
                    },
                    "message": "More than one semicolon",
                    "severity": 2,
                    "code": "W014/multiple-semicolons",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 7, "character": 0},
                        "end": {"line": 7, "character": 156},
                    },
                    "message": "Wrong whitespace around operator -",
                    "severity": 2,
                    "code": "W022/whitespace-op-negative",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 9, "character": 0},
                        "end": {"line": 9, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 11, "character": 0},
                        "end": {"line": 11, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 11, "character": 0},
                        "end": {"line": 11, "character": 153},
                    },
                    "message": "Wrong whitespace around operator +",
                    "severity": 2,
                    "code": "W020/whitespace-op-plus",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 12, "character": 0},
                        "end": {"line": 12, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 13, "character": 0},
                        "end": {"line": 13, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 14, "character": 0},
                        "end": {"line": 14, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 14, "character": 0},
                        "end": {"line": 14, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 14, "character": 0},
                        "end": {"line": 14, "character": 154},
                    },
                    "message": "Wrong whitespace around operator -",
                    "severity": 2,
                    "code": "W019/whitespace-op-minus",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 15, "character": 0},
                        "end": {"line": 15, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 15, "character": 0},
                        "end": {"line": 15, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 16, "character": 0},
                        "end": {"line": 16, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 16, "character": 0},
                        "end": {"line": 16, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 16, "character": 0},
                        "end": {"line": 16, "character": 154},
                    },
                    "message": "Wrong whitespace around operator ^",
                    "severity": 2,
                    "code": "W030/whitespace-op-power",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 17, "character": 0},
                        "end": {"line": 17, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 17, "character": 0},
                        "end": {"line": 17, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 17, "character": 0},
                        "end": {"line": 17, "character": 159},
                    },
                    "message": "Wrong whitespace around operator <>",
                    "severity": 2,
                    "code": "W031/whitespace-op-not-equal",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 19, "character": 0},
                        "end": {"line": 19, "character": 139},
                    },
                    "message": "Trailing whitespace",
                    "severity": 2,
                    "code": "W007/trailing-whitespace",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 19, "character": 0},
                        "end": {"line": 19, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 19, "character": 0},
                        "end": {"line": 19, "character": 157},
                    },
                    "message": "Wrong whitespace around operator ..",
                    "severity": 2,
                    "code": "W032/whitespace-double-dot",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 20, "character": 0},
                        "end": {"line": 20, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 20, "character": 0},
                        "end": {"line": 20, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 21, "character": 0},
                        "end": {"line": 21, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 21, "character": 0},
                        "end": {"line": 21, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 21, "character": 0},
                        "end": {"line": 21, "character": 154},
                    },
                    "message": "Wrong whitespace around operator -",
                    "severity": 2,
                    "code": "W019/whitespace-op-minus",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 23, "character": 0},
                        "end": {"line": 23, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 24, "character": 0},
                        "end": {"line": 24, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 24, "character": 0},
                        "end": {"line": 24, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 24, "character": 0},
                        "end": {"line": 24, "character": 154},
                    },
                    "message": "Wrong whitespace around operator -",
                    "severity": 2,
                    "code": "W019/whitespace-op-minus",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 25, "character": 0},
                        "end": {"line": 25, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 26, "character": 0},
                        "end": {"line": 26, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 26, "character": 0},
                        "end": {"line": 26, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 26, "character": 0},
                        "end": {"line": 26, "character": 154},
                    },
                    "message": "Wrong whitespace around operator -",
                    "severity": 2,
                    "code": "W019/whitespace-op-minus",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 27, "character": 0},
                        "end": {"line": 27, "character": 156},
                    },
                    "message": "Wrong whitespace around operator :=",
                    "severity": 2,
                    "code": "W016/whitespace-op-assign",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 28, "character": 0},
                        "end": {"line": 28, "character": 160},
                    },
                    "message": "Unaligned assignments in consecutive lines",
                    "severity": 2,
                    "code": "W004/align-assignments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 28, "character": 0},
                        "end": {"line": 28, "character": 156},
                    },
                    "message": "Wrong whitespace around operator :=",
                    "severity": 2,
                    "code": "W016/whitespace-op-assign",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 29, "character": 0},
                        "end": {"line": 29, "character": 160},
                    },
                    "message": "Unaligned assignments in consecutive lines",
                    "severity": 2,
                    "code": "W004/align-assignments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 32, "character": 0},
                        "end": {"line": 32, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 32, "character": 0},
                        "end": {"line": 32, "character": 150},
                    },
                    "message": "No space allowed after bracket",
                    "severity": 2,
                    "code": "W012/space-after-bracket",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 33, "character": 0},
                        "end": {"line": 33, "character": 163},
                    },
                    "message": "Unaligned comments in consecutive lines",
                    "severity": 2,
                    "code": "W005/align-trailing-comments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 33, "character": 0},
                        "end": {"line": 33, "character": 164},
                    },
                    "message": "At least 2 spaces before comment",
                    "severity": 2,
                    "code": "W009/not-enough-space-before-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 39, "character": 0},
                        "end": {"line": 39, "character": 137},
                    },
                    "message": "Too long line (81 / 80)",
                    "severity": 2,
                    "code": "W002/line-too-long",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 41, "character": 0},
                        "end": {"line": 41, "character": 139},
                    },
                    "message": "Trailing whitespace",
                    "severity": 2,
                    "code": "W007/trailing-whitespace",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 42, "character": 0},
                        "end": {"line": 42, "character": 160},
                    },
                    "message": "Bad indentation: found 0 but expected at least 2",
                    "severity": 2,
                    "code": "W003/indentation",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 46, "character": 0},
                        "end": {"line": 46, "character": 143},
                    },
                    "message": "More than one semicolon",
                    "severity": 2,
                    "code": "W014/multiple-semicolons",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 46, "character": 0},
                        "end": {"line": 46, "character": 173},
                    },
                    "message": "Keywords 'function' and 'local' in the same line",
                    "severity": 2,
                    "code": "W018/function-local-same-line",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 49, "character": 0},
                        "end": {"line": 49, "character": 145},
                    },
                    "message": "No space after comment",
                    "severity": 2,
                    "code": "W008/no-space-after-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 54, "character": 0},
                        "end": {"line": 54, "character": 145},
                    },
                    "message": "No space after comment",
                    "severity": 2,
                    "code": "W008/no-space-after-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 57, "character": 0},
                        "end": {"line": 57, "character": 145},
                    },
                    "message": "No space after comment",
                    "severity": 2,
                    "code": "W008/no-space-after-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 58, "character": 0},
                        "end": {"line": 58, "character": 145},
                    },
                    "message": "No space after comment",
                    "severity": 2,
                    "code": "W008/no-space-after-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 61, "character": 0},
                        "end": {"line": 61, "character": 145},
                    },
                    "message": "No space after comment",
                    "severity": 2,
                    "code": "W008/no-space-after-comment",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 68, "character": 0},
                        "end": {"line": 68, "character": 160},
                    },
                    "message": "Unaligned assignments in consecutive lines",
                    "severity": 2,
                    "code": "W004/align-assignments",
                    "source": "gaplint",
                },
                {
                    "range": {
                        "start": {"line": 68, "character": 0},
                        "end": {"line": 68, "character": 156},
                    },
                    "message": "Exactly one space required after comma",
                    "severity": 2,
                    "code": "W010/space-after-comma",
                    "source": "gaplint",
                },
            ],
        }

    assert_that(actual, is_(expected))
