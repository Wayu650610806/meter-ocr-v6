"""Validate the pinned release, paths and every file before building."""
import hashlib
import json
from pathlib import Path
import stat
import sys
from zipfile import ZipFile

pin = json.loads((Path(__file__).resolve().parents[1] / 'build-context.json').read_text())
archive, destination = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
with archive.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest() == pin['sha256'], 'Release archive hash mismatch'
destination.mkdir(parents=True, exist_ok=True)
with ZipFile(archive) as source:
    members = source.infolist()
    assert len({item.filename for item in members}) == len(members), 'Duplicate ZIP member'
    for item in members:
        assert '\\' not in item.filename and item.filename.startswith('meter-v6/'), 'Unexpected ZIP path'
        assert (destination / item.filename).resolve().is_relative_to(destination), 'Unsafe ZIP path'
        assert not stat.S_ISLNK(item.external_attr >> 16), 'ZIP symlinks are not allowed'
    source.extractall(destination)
root = destination / 'meter-v6'
manifest = json.loads((root / 'manifest.json').read_text())
assert manifest['purpose'] == 'note16_water_final_electric_v5_v1'
for name, digest in manifest['files'].items():
    path = (root / name).resolve()
    assert path.is_relative_to(root), name
    with path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == digest, name
print(f'Archive and {len(manifest["files"])} manifest files verified. No dataset images included.')
