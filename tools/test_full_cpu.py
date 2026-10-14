"""Actual water/electric inference plus API requests on generated images, no human data."""
import io,json,os,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ['OCR_API_KEY']='ci-synthetic-only'
os.environ['METER_PRELOAD']='1'
from meter_delivery.runtime import validate
from tools.stage_verified_hf_snapshot import stage_verified
root=Path(os.environ.get('METER_BUNDLE','/app'));manifest=validate(root);spec=manifest['model_staging']
stage_verified(spec['model'],spec['revision'],Path(os.environ['METER_HUB_CACHE']),Path(os.environ['METER_MODEL_CACHE']),Path(os.environ['METER_WORKDIR']))
print('Verified Qwen base; loading actual API',flush=True)
from meter_delivery.app_v6 import app,PIPELINE
from fastapi.testclient import TestClient
from PIL import Image,ImageDraw
im=Image.new('RGB',(320,240),'white');draw=ImageDraw.Draw(im);draw.text((25,55),'001234',fill='black',font_size=32);draw.text((25,165),'A001',fill='black',font_size=32)
body=io.BytesIO();im.save(body,'PNG');headers={'X-API-Key':'ci-synthetic-only'}
with TestClient(app) as client:
    h=client.get('/health');assert h.status_code==200 and h.json()['runtime']['water']['loaded']
    assert client.post('/uploadimage',files={'file':('synthetic.png',body.getvalue(),'image/png')}).status_code in (401,403)
    response=client.post('/uploadimage',headers=headers,files={'file':('synthetic.png',body.getvalue(),'image/png')})
    assert response.status_code in (200,422),response.text
    assert 'data' in response.json() or 'candidate' in response.json(),response.text
    proposal=client.post('/annotation-proposal',headers=headers,files={'file':('synthetic.png',body.getvalue(),'image/png')})
    assert proposal.status_code==200 and proposal.json()['annotation_status']=='draft',proposal.text
    print('Real detector and API requests passed',flush=True)
    started=time.monotonic();water=PIPELINE.reader.water_predict(im,im,'full_image')
    assert water['output_tokens']>0 and isinstance(water['raw'],str)
    assert water['status'] in ('ok','needs_review'),water
    assert 'generation_token_limit' not in water['warnings'],water
    report={'status':'passed','health':h.json(),'api_upload_status':response.status_code,'annotation_proposal_status':proposal.status_code,'water_generation':water,'water_seconds':time.monotonic()-started,'smoke_generation_token_limit':128,'scope':'Full-length synthetic CPU runtime test; not dataset accuracy or GPU execution'}
    target=Path(os.environ.get('SMOKE_REPORT','/tmp/v6-full-smoke.json'));target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
