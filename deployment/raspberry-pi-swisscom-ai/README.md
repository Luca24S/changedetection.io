# Raspberry Pi deployment with Swisscom AI proxy

This setup runs `changedetection.io` and a small internal OpenAI-compatible proxy.
The real Swisscom AI key stays in the proxy container only.

## Files

- `docker-compose.yml`: starts changedetection.io and the internal proxy.
- `.env.example`: copy to `.env` and insert the Swisscom AI key.
- `swisscom-ai-proxy/`: tiny Flask/Gunicorn proxy that forwards chat completions to Swisscom AI.

## Raspberry Pi setup

Use a 64-bit Raspberry Pi OS install where possible.

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Log out and back in, then copy this folder to the Raspberry Pi.

## Configure

```bash
cd raspberry-pi-swisscom-ai
cp .env.example .env
nano .env
chmod 600 .env
```

Set:

```bash
SWISSCOM_API_KEY=your-real-key
SWISSCOM_BASE_URL=https://code.myai.swisscom.ch/v1
SWISSCOM_MODEL=qwen3.5-397b-a17b
```

## Start

```bash
docker compose up -d --build
docker compose logs -f
```

Open:

```text
http://RASPBERRY_PI_IP:5000
```

Find the Raspberry Pi IP with:

```bash
hostname -I
```

## changedetection.io AI settings

In the UI, go to:

```text
Settings -> AI / LLM -> Provider
```

Use:

```text
Provider: OpenAI-compatible (vLLM, LM Studio, llama.cpp)
API Key: local-proxy
API Base URL: http://swisscom-ai:8080/v1
Model: openai/qwen3.5-397b-a17b
```

Then save and run `Test connection`.

If model loading does not return anything, type the model manually. The proxy always sends
`SWISSCOM_MODEL` to Swisscom, so the value in changedetection.io is mainly for LiteLLM routing.

## Isolation notes

- The proxy is not published with `ports`; it is only reachable inside the Docker network.
- changedetection.io only receives a dummy key (`local-proxy`).
- The real Swisscom key is stored in `.env` and injected only into the proxy container.
- `ALLOW_IANA_RESTRICTED_ADDRESSES=true` is required because changedetection.io blocks private/internal LLM API base URLs by default.

