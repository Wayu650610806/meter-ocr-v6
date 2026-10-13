import json
from pathlib import Path
import sys

manifest = json.loads(Path(sys.argv[1]).read_text())
assert 'manifests' in manifest, 'Expected OCI index with provenance'
platforms = [entry['platform'] for entry in manifest['manifests']
             if entry.get('annotations', {}).get('vnd.docker.reference.type') != 'attestation-manifest']
assert len(platforms) == 1 and platforms[0]['os'] == 'linux' and platforms[0]['architecture'] == 'amd64', platforms
print('Verified: one runnable platform, linux/amd64')
