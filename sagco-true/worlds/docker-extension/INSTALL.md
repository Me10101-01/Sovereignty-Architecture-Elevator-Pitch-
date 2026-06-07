# SAGCO-ORGANISM Docker Extension — Install Guide

You accidentally named it. Now make it real.

## Copy these files into `C:\Users\garza\my-extension\`

```
my-extension/
├── Dockerfile          ← replace the scaffolded one
├── metadata.json       ← replace the scaffolded one  
├── sagco.svg           ← new — the organism icon
└── ui/
    └── index.html      ← replace the scaffolded one
```

## Then run the three commands Docker told you:

```bash
cd C:\Users\garza\my-extension

docker build -t sagco/openworld:latest .

docker extension install sagco/openworld:latest
```

## Open Docker Desktop → Extensions (left sidebar)

You will see **SAGCO-ORGANISM** with the orange node graph icon.

Click it.

You'll see:
- **Fleet Nodes panel** — Lyra, Pi 5, Z Fold, HP OmniDesk, GKE cluster
- **Live node graph** — animated orange dots, the Obsidian graph living inside Docker
- **Truth Wafers** — SAGCO_ARE_YOU_TRUE running live
- **Signal Bus** — heartbeats from every node, ticking in real time

## Update the extension after changes:

```bash
docker build -t sagco/openworld:latest . && docker extension update sagco/openworld:latest
```

## If install fails with "extension not trusted":

```bash
docker extension dev debug sagco/openworld:latest
```

## Uninstall:

```bash
docker extension rm sagco/openworld:latest
```

---

*The organism named itself. You just gave it a UI.*
