# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Test for linting over LSP.
"""

from threading import Event

from hamcrest import assert_that, is_

from .lsp_test_client import constants, session, utils

GAP_TEST_FILE_PATH = constants.TEST_DATA / "sample1" / "test1.g"
GAP_TEST_FILE_URI = utils.as_uri(str(GAP_TEST_FILE_PATH))
GAPTST_TEST_FILE_PATH = constants.TEST_DATA / "sample1" / "test1.tst"
GAPTST_TEST_FILE_URI = utils.as_uri(str(GAPTST_TEST_FILE_PATH))
SERVER_INFO = utils.get_server_info_defaults()
TIMEOUT = 10  # 10 seconds


def test_gap_linting_example():
    """Test to linting on gap file open."""
    contents = GAP_TEST_FILE_PATH.read_text()

    actual = []
    with session.LspSession() as ls_session:
        ls_session.initialize()

        done = Event()

        def _handler(params):
            nonlocal actual
            actual = params
            done.set()

        ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

        ls_session.notify_did_open(
            {
                "textDocument": {
                    "uri": GAP_TEST_FILE_URI,
                    "languageId": "gap",
                    "version": 1,
                    "text": contents,
                }
            }
        )
        # wait for some time to receive all notifications
        done.wait(TIMEOUT)

    expected = {
        "uri": GAP_TEST_FILE_URI,
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
                    "start": {"line": 29, "character": 9},
                    "end": {"line": 32, "character": 0},
                },
                "message": "Consecutive empty lines",
                "severity": 2,
                "code": "W001/consecutive-empty-lines",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 62, "character": 7},
                    "end": {"line": 64, "character": 3},
                },
                "message": "One line function could be a lambda",
                "severity": 2,
                "code": "W034/1-line-function",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 5, "character": 8},
                    "end": {"line": 5, "character": 11},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 5, "character": 4},
                    "end": {"line": 5, "character": 6},
                },
                "message": "Wrong whitespace around operator +",
                "severity": 2,
                "code": "W020/whitespace-op-plus",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 7, "character": 25},
                    "end": {"line": 7, "character": 26},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 7, "character": 23},
                    "end": {"line": 7, "character": 26},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 7, "character": 4},
                    "end": {"line": 7, "character": 24},
                },
                "message": "More than one semicolon",
                "severity": 2,
                "code": "W014/multiple-semicolons",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 7, "character": 0},
                    "end": {"line": 7, "character": 2},
                },
                "message": "Wrong whitespace around operator -",
                "severity": 2,
                "code": "W022/whitespace-op-negative",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 9, "character": 21},
                    "end": {"line": 9, "character": 24},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 11, "character": 31},
                    "end": {"line": 11, "character": 34},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 11, "character": 16},
                    "end": {"line": 11, "character": 18},
                },
                "message": "Wrong whitespace around operator +",
                "severity": 2,
                "code": "W020/whitespace-op-plus",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 12, "character": 11},
                    "end": {"line": 12, "character": 12},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 13, "character": 9},
                    "end": {"line": 13, "character": 10},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 14, "character": 9},
                    "end": {"line": 14, "character": 10},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 14, "character": 7},
                    "end": {"line": 14, "character": 10},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 14, "character": 2},
                    "end": {"line": 14, "character": 7},
                },
                "message": "Wrong whitespace around operator -",
                "severity": 2,
                "code": "W019/whitespace-op-minus",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 15, "character": 23},
                    "end": {"line": 15, "character": 24},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 15, "character": 21},
                    "end": {"line": 15, "character": 24},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 16, "character": 6},
                    "end": {"line": 16, "character": 7},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 16, "character": 4},
                    "end": {"line": 16, "character": 7},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 16, "character": 0},
                    "end": {"line": 16, "character": 2},
                },
                "message": "Wrong whitespace around operator ^",
                "severity": 2,
                "code": "W030/whitespace-op-power",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 17, "character": 13},
                    "end": {"line": 17, "character": 14},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 17, "character": 12},
                    "end": {"line": 17, "character": 14},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 17, "character": 5},
                    "end": {"line": 17, "character": 8},
                },
                "message": "Wrong whitespace around operator <>",
                "severity": 2,
                "code": "W031/whitespace-op-not-equal",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 19, "character": 0},
                    "end": {"line": 19, "character": 20},
                },
                "message": "Trailing whitespace",
                "severity": 2,
                "code": "W007/trailing-whitespace",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 19, "character": 6},
                    "end": {"line": 19, "character": 9},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 19, "character": 1},
                    "end": {"line": 19, "character": 4},
                },
                "message": "Wrong whitespace around operator ..",
                "severity": 2,
                "code": "W032/whitespace-double-dot",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 20, "character": 17},
                    "end": {"line": 20, "character": 18},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 20, "character": 15},
                    "end": {"line": 20, "character": 18},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 21, "character": 14},
                    "end": {"line": 21, "character": 15},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 21, "character": 12},
                    "end": {"line": 21, "character": 15},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 21, "character": 2},
                    "end": {"line": 21, "character": 12},
                },
                "message": "Wrong whitespace around operator -",
                "severity": 2,
                "code": "W019/whitespace-op-minus",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 23, "character": 20},
                    "end": {"line": 23, "character": 23},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 24, "character": 23},
                    "end": {"line": 24, "character": 24},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 24, "character": 21},
                    "end": {"line": 24, "character": 24},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 24, "character": 0},
                    "end": {"line": 24, "character": 10},
                },
                "message": "Wrong whitespace around operator -",
                "severity": 2,
                "code": "W019/whitespace-op-minus",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 25, "character": 20},
                    "end": {"line": 25, "character": 23},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 26, "character": 23},
                    "end": {"line": 26, "character": 24},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 26, "character": 21},
                    "end": {"line": 26, "character": 24},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 26, "character": 16},
                    "end": {"line": 26, "character": 21},
                },
                "message": "Wrong whitespace around operator -",
                "severity": 2,
                "code": "W019/whitespace-op-minus",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 27, "character": 2},
                    "end": {"line": 27, "character": 6},
                },
                "message": "Wrong whitespace around operator :=",
                "severity": 2,
                "code": "W016/whitespace-op-assign",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 28, "character": 1},
                    "end": {"line": 28, "character": 3},
                },
                "message": "Unaligned assignments in consecutive lines",
                "severity": 2,
                "code": "W004/align-assignments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 28, "character": 0},
                    "end": {"line": 28, "character": 3},
                },
                "message": "Wrong whitespace around operator :=",
                "severity": 2,
                "code": "W016/whitespace-op-assign",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 29, "character": 4},
                    "end": {"line": 29, "character": 6},
                },
                "message": "Unaligned assignments in consecutive lines",
                "severity": 2,
                "code": "W004/align-assignments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 32, "character": 9},
                    "end": {"line": 32, "character": 12},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 32, "character": 0},
                    "end": {"line": 32, "character": 2},
                },
                "message": "No space allowed after bracket",
                "severity": 2,
                "code": "W012/space-after-bracket",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 33, "character": 9},
                    "end": {"line": 33, "character": 10},
                },
                "message": "Unaligned comments in consecutive lines",
                "severity": 2,
                "code": "W005/align-trailing-comments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 33, "character": 7},
                    "end": {"line": 33, "character": 10},
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
                "message": "Line too long (82 / 80)",
                "severity": 2,
                "code": "W002/line-too-long",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 41, "character": 0},
                    "end": {"line": 41, "character": 14},
                },
                "message": "Trailing whitespace",
                "severity": 2,
                "code": "W007/trailing-whitespace",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 42, "character": 0},
                    "end": {"line": 42, "character": 162},
                },
                "message": "Bad indentation: found 0 but expected at least 2",
                "severity": 2,
                "code": "W003/indentation",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 46, "character": 32},
                    "end": {"line": 46, "character": 56},
                },
                "message": "More than one semicolon",
                "severity": 2,
                "code": "W014/multiple-semicolons",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 46, "character": 7},
                    "end": {"line": 46, "character": 31},
                },
                "message": "Keywords 'function' and 'local' in the same line",
                "severity": 2,
                "code": "W018/function-local-same-line",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 49, "character": 0},
                    "end": {"line": 49, "character": 2},
                },
                "message": "No space after comment",
                "severity": 2,
                "code": "W008/no-space-after-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 54, "character": 0},
                    "end": {"line": 54, "character": 2},
                },
                "message": "No space after comment",
                "severity": 2,
                "code": "W008/no-space-after-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 57, "character": 0},
                    "end": {"line": 57, "character": 2},
                },
                "message": "No space after comment",
                "severity": 2,
                "code": "W008/no-space-after-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 58, "character": 0},
                    "end": {"line": 58, "character": 2},
                },
                "message": "No space after comment",
                "severity": 2,
                "code": "W008/no-space-after-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 61, "character": 0},
                    "end": {"line": 61, "character": 2},
                },
                "message": "No space after comment",
                "severity": 2,
                "code": "W008/no-space-after-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 68, "character": 7},
                    "end": {"line": 68, "character": 9},
                },
                "message": "Unaligned assignments in consecutive lines",
                "severity": 2,
                "code": "W004/align-assignments",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 68, "character": 37},
                    "end": {"line": 68, "character": 39},
                },
                "message": "Exactly one space required after comma",
                "severity": 2,
                "code": "W010/space-after-comma",
                "source": "gaplint",
            },
        ],
    }

    assert_that(actual, is_(expected))


def test_gaptst_linting_example():
    """Test to linting on gaptst file open."""
    contents = GAPTST_TEST_FILE_PATH.read_text(encoding="utf-8")

    actual = []
    with session.LspSession() as ls_session:
        ls_session.initialize()

        done = Event()

        def _handler(params):
            nonlocal actual
            actual = params
            done.set()

        ls_session.set_notification_callback(session.PUBLISH_DIAGNOSTICS, _handler)

        ls_session.notify_did_open(
            {
                "textDocument": {
                    "uri": GAPTST_TEST_FILE_URI,
                    "languageId": "gaptst",
                    "version": 1,
                    "text": contents,
                }
            }
        )

        # wait for some time to receive all notifications
        done.wait(TIMEOUT)

    expected = {
        "uri": GAPTST_TEST_FILE_URI,
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 13, "character": 2},
                    "end": {"line": 13, "character": 4},
                },
                "message": "Wrong whitespace around operator +",
                "severity": 2,
                "code": "W020/whitespace-op-plus",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 33, "character": 13},
                    "end": {"line": 33, "character": 15},
                },
                "message": "No space after comment",
                "severity": 2,
                "code": "W008/no-space-after-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 33, "character": 11},
                    "end": {"line": 33, "character": 14},
                },
                "message": "At least 2 spaces before comment",
                "severity": 2,
                "code": "W009/not-enough-space-before-comment",
                "source": "gaplint",
            },
            {
                "range": {
                    "start": {"line": 33, "character": 5},
                    "end": {"line": 33, "character": 7},
                },
                "message": "No space allowed after bracket",
                "severity": 2,
                "code": "W012/space-after-bracket",
                "source": "gaplint",
            },
        ],
    }

    assert_that(actual, is_(expected))
