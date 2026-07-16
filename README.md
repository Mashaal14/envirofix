# 🔧 EnviroFix

**AI-Powered Kali Linux Environment Intelligence Platform**

EnviroFix is a local, AI‑powered environment monitoring and diagnostic platform built exclusively for Kali Linux. It runs silently as a background daemon, continuously scanning the system for broken packages, expired GPG keys, missing kernel headers, library conflicts, and network issues. When problems are detected, it uses locally‑running AI models (DeepSeek‑R1 and Qwen2.5‑Coder) to explain root causes, provide precise fix commands, and teach the user why the issue occurred.

---

## ✨ Features

- **5 Scanner Modules** – APT, GPG, Kernel, Libraries, Network
- **AI Diagnosis** – DeepSeek‑R1 (8B) explains root causes
- **AI Teaching** – Qwen2.5‑Coder (7B) explains fixes in plain English
- **RAG System** – ChromaDB with live Kali documentation (refreshed every 6 hours)
- **Dark Theme Dashboard** – Grafana‑style UI with real‑time health metrics
- **100% Local** – No data leaves your machine. No cloud dependency.
- **One‑Command Install** – `curl -fsSL https://envirofix.io/install | bash`
- **Dockerized** – Runs on any Linux system (Kali, Ubuntu, Debian)

---

## 📋 Table of Contents

- [System Requirements](#-system-requirements)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Dependencies](#-dependencies)
- [AI Models](#-ai-models)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Troubleshooting](#-troubleshooting)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🖥️ System Requirements

### Minimum (Mock AI Mode – Demo)
| Component | Requirement |
|-----------|-------------|
| OS | Linux (Kali, Ubuntu 22.04+, Debian 12+) |
| CPU | 1 vCPU |
| RAM | 1 GB |
| Storage | 30 GB SSD |
| Docker | 24.0+ |
| Docker Compose | 2.20+ |

### Recommended (Full AI Mode)
| Component | Requirement |
|-----------|-------------|
| OS | Linux (Kali, Ubuntu 22.04+, Debian 12+) |
| CPU | 4+ vCPUs |
| RAM | 16 GB (minimum) / 32 GB (recommended) |
| Storage | 50 GB+ SSD |
| Docker | 24.0+ |
| Docker Compose | 2.20+ |

---

## 🚀 Quick Start

```bash
# One‑command installation (recommended)
curl -fsSL https://raw.githubusercontent.com/Mashaal14/envirofix/main/install.sh | sudo bash

# Or manually:
git clone https://github.com/Mashaal14/envirofix.git /opt/envirofix
cd /opt/envirofix
docker-compose up -d

# Open dashboard: http://<your-server-ip>:3000
