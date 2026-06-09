# Raspberry Pi deployment with Swisscom AI proxy

This setup runs `changedetection.io` and a small internal OpenAI-compatible proxy.
The real Swisscom AI key stays in the proxy container only.

## Files

- `docker-compose.yml`: starts changedetection.io and the internal proxy.
- `.env.example`: copy to `.env` and insert the Swisscom AI key.
- `swisscom-ai-proxy/`: tiny Flask/Gunicorn proxy that forwards chat completions to Swisscom AI.

## What this deployment adds

- A Raspberry Pi specific Docker Compose setup.
- A separate `swisscom-ai` proxy container that speaks an OpenAI-compatible API to changedetection.io.
- Isolation for the real Swisscom AI key: changedetection.io only sees the dummy key `local-proxy`.
- A private Docker network between `changedetection` and `swisscom-ai`.
- Persistent changedetection.io data in `./datastore`.
- Automatic container restart with `restart: unless-stopped`.
- `.gitignore` rules to avoid committing `.env` and runtime data.

This deployment does not modify the changedetection.io application code.

## Raspberry Pi setup

Use a 64-bit Raspberry Pi OS install where possible.

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Log out and back in, then copy this folder to the Raspberry Pi.

Recommended dedicated user layout:

```bash
sudo adduser --disabled-password --gecos "" changedetection
sudo usermod -aG docker changedetection
sudo mkdir -p /opt/changedetection
sudo chown -R changedetection:changedetection /opt/changedetection
sudo -iu changedetection
cd /opt/changedetection
git clone https://github.com/dgtlmoon/changedetection.io.git
cd changedetection.io/deployment/raspberry-pi-swisscom-ai
```

If you use your own fork, replace the `git clone` URL with your fork URL.

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

For `Token multiplier for local reasoning models`, start with:

```text
5
```

Raise it to `8` or `10` only if summaries or test responses come back empty or truncated.
Lower it if you need tighter cost control.

If model loading does not return anything, type the model manually. The proxy always sends
`SWISSCOM_MODEL` to Swisscom, so the value in changedetection.io is mainly for LiteLLM routing.

## Routine commands

From the deployment directory:

```bash
docker compose ps
docker compose logs -f
docker compose logs --tail=100 changedetection
docker compose logs --tail=100 swisscom-ai
docker compose restart
docker compose down
docker compose up -d --build
```

On the Raspberry Pi with the dedicated user:

```bash
sudo -iu changedetection
cd /opt/changedetection/changedetection.io/deployment/raspberry-pi-swisscom-ai
```

If your clone is in the home directory instead, use:

```bash
cd ~/changedetection.io/deployment/raspberry-pi-swisscom-ai
```

## Updating

Update the repository and containers:

```bash
sudo -iu changedetection
cd /opt/changedetection/changedetection.io
git pull
cd deployment/raspberry-pi-swisscom-ai
docker compose pull
docker compose up -d --build
```

Check the result:

```bash
docker compose ps
docker compose logs --tail=100 changedetection
docker compose logs --tail=100 swisscom-ai
```

The local `.env` file and `datastore/` directory are not tracked by Git, so normal
updates preserve the Swisscom key and changedetection.io data.

Before a bigger update, make a datastore backup:

```bash
cd /opt/changedetection/changedetection.io/deployment/raspberry-pi-swisscom-ai
docker compose down
cp -a datastore "datastore.backup.$(date +%Y%m%d-%H%M%S)"
docker compose up -d
```

## Isolation notes

- The proxy is not published with `ports`; it is only reachable inside the Docker network.
- changedetection.io only receives a dummy key (`local-proxy`).
- The real Swisscom key is stored in `.env` and injected only into the proxy container.
- `ALLOW_IANA_RESTRICTED_ADDRESSES=true` is required because changedetection.io blocks private/internal LLM API base URLs by default.
