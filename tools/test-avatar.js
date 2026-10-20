const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { avatarFor, FILES } = require('../src/avatar');

for (const f of FILES) assert(fs.existsSync(path.join(__dirname, '../web/avatars', f)), `missing ${f}`);
assert.strictEqual(avatarFor('user-a', 0), avatarFor('user-a', 0), 'same user, same face');
for (let n = 0; n < FILES.length; n++) {
  assert.notStrictEqual(avatarFor('user-a', n), avatarFor('user-a', n + 1), 'regenerate always changes the face');
}
const faces = new Set(Array.from({ length: 200 }, (_, i) => avatarFor('user-' + i, 0)));
assert(faces.size >= FILES.length * 0.8, `users should spread over the set, got ${faces.size}`);
console.log('avatar ok');
