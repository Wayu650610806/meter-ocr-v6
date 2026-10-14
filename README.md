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

The r4 build includes setuptools in both Paddle environments. CPU builds execute the electric models on synthetic pixels before publication. GPU builds check Paddle CUDA support and ONNX CUDA-provider registration without executing CUDA kernels. After the CPU image is published, CI loads the actual API and water model, checks health/auth/upload/annotation-proposal, and runs a bounded eight-token water generation smoke. It uses swap on the disposable hosted runner when necessary; production dtype and token limits are unchanged.

These checks are not dataset accuracy, a latency benchmark, or proof of GPU inference. The hosted runner has no GPU. Water VLM confidence is uncalibrated; parsing complete fields does not itself establish high confidence. The image contains `tools/smoke_v6_electric.py --device gpu` and `tools/smoke_v6_full.py` for execution with `docker run --gpus all --entrypoint python` on a real NVIDIA host.

The existing Hugging Face Space uses CPU through a small Dockerfile wrapper. Updating a Docker Hub tag does not rebuild an already running Space automatically.

Workflow uses pinned commits of [Docker's official GitHub Actions](https://docs.docker.com/guides/gha/).
