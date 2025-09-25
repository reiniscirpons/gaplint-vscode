// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

import { assert } from 'chai';
import * as sinon from 'sinon';
import * as vscodeapi from '../../../../common/vscodeapi';
import { getDocumentSelector } from '../../../../common/utilities';

suite('Document Selector Tests', () => {
  let isVirtualWorkspaceStub: sinon.SinonStub;
  setup(() => {
    isVirtualWorkspaceStub = sinon.stub(vscodeapi, 'isVirtualWorkspace');
    isVirtualWorkspaceStub.returns(false);
  });
  teardown(() => {
    sinon.restore();
  });

  test('Document selector default', () => {
    const selector = getDocumentSelector();
    assert.deepStrictEqual(selector, [
      { scheme: 'file', language: 'gap' },
      { scheme: 'untitled', language: 'gap' },
      { scheme: 'vscode-notebook', language: 'gap' },
      { scheme: 'vscode-notebook-cell', language: 'gap' },
      { scheme: 'file', language: 'gaptst' },
      { scheme: 'untitled', language: 'gaptst' },
      { scheme: 'vscode-notebook', language: 'gaptst' },
      { scheme: 'vscode-notebook-cell', language: 'gaptst' },
      { scheme: 'file', pattern: '*.{g,gi,gd,tst}' },
      { scheme: 'untitled', pattern: '*.{g,gi,gd,tst}' },
      { scheme: 'vscode-notebook', pattern: '*.{g,gi,gd,tst}' },
      { scheme: 'vscode-notebook-cell', pattern: '*.{g,gi,gd,tst}' },
    ]);
  });
  test('Document selector virtual workspace', () => {
    isVirtualWorkspaceStub.returns(true);
    const selector = getDocumentSelector();
    assert.deepStrictEqual(selector, [{ language: 'python' }]);
  });
});
