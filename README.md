# Meter OCR v6 — cloud Docker build

Builds and publishes **linux/amd64 only**, sequentially:

- `wayu199/meter-ocr:v6-cpu`: all model inference on CPU.
- `wayu199/meter-ocr:v6-gpu`: all model inference on CUDA; startup fails if GPU support is unavailable.

NOTE16 routes each image to Final water Qwen or the legacy v5 electric reader. The v5 API endpoints and input/output serialization are preserved. Image preprocessing and CTC decoding still run on CPU in both variants.

## Run

1. Set repository Actions secret `DOCKERHUB_TOKEN` to a Docker Hub access token with push access to `wayu199/meter-ocr`.
2. Open **Actions → Build and publish Meter OCR v6 → Run workflow → both**.
3. Check both jobs and their published image digests. Rerun just `cpu` or `gpu` if only one failed.

GitHub downloads the pinned Release asset, verifies its SHA256 and every manifest file, and performs the complete Docker build/push on the hosted runner. You may shut down your computer after dispatch. No Docker Desktop or local model inference is needed. Private repositories use the account's Actions allowance.

The Release asset contains deployment code and selected weights, without dataset images, human annotations or credentials. Dockerfiles and dependency pins are inside the verified build archive. Old `v4`, `v5` and `latest` tags are never changed.

## Start the API

Set `OCR_API_KEY` in the host environment, then:

```sh
docker run --rm -p 8080:8080 -e OCR_API_KEY -v meter-v6-models:/models wayu199/meter-ocr:v6-cpu
docker run --rm --gpus all -p 8080:8080 -e OCR_API_KEY -v meter-v6-models:/models wayu199/meter-ocr:v6-gpu
```

First startup downloads the pinned public Qwen base (~4 GB), verifies its hashes, and caches it in `/models`. API authentication keys are runtime secrets and are not baked into images. One worker and one concurrent inference are the defaults.

Successful CI confirms build/publication and platform, not accuracy or GPU inference: the hosted runner has no GPU. No new dataset benchmark is requested. Water VLM confidence is uncalibrated; parsing complete fields does not itself establish high confidence. See `README_TH.md` inside the release for API details.

Hugging Face remains deferred until both Docker Hub tags are ready. It will use CPU and one Dockerfile based on `v6-cpu`.

Workflow uses pinned commits of [Docker's official GitHub Actions](https://docs.docker.com/guides/gha/).
