#!/usr/bin/env python3
"""
ASV V3 monorepo scaffold generator
- Creates folders + placeholder files for the full repo structure.
- Safe by default: won't overwrite existing files unless --overwrite is used.

Usage:
  python scaffold_asv_repo.py --root ./asv
  python scaffold_asv_repo.py --root ./asv --overwrite
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Dict


REPO_STRUCTURE: Dict[str, str] = {
    # Top-level
    "README.md": "# ASV\n\nMonorepo scaffold.\n",
    "LICENSE": "TODO: rAdd license text.\n",
    ".env.example": "# Example env\n",
    ".editorconfig": "root = true\n\n[*]\nend_of_line = lf\ninsert_final_newline = true\ncharset = utf-8\n",
    ".gitignore": ".env\n.DS_Store\n__pycache__/\n*.pyc\nnode_modules/\nbuild/\ndist/\n.ml_data/\n",
    "docker-compose.yml": "version: '3.9'\nservices: {}\n",
    "Makefile": "help:\n\t@echo \"ASV repo scaffold\"\n",
    "CHANGELOG.md": "# Changelog\n\n",
    "SECURITY.md": "# Security\n\nReport issues responsibly.\n",

    # GitHub
    ".github/workflows/ci.yml": "name: ci\non: [push, pull_request]\njobs: {}\n",
    ".github/workflows/lint.yml": "name: lint\non: [push, pull_request]\njobs: {}\n",
    ".github/workflows/tests.yml": "name: tests\non: [push, pull_request]\njobs: {}\n",
    ".github/workflows/security-scan.yml": "name: security-scan\non: [push, pull_request]\njobs: {}\n",
    ".github/workflows/release.yml": "name: release\non:\n  push:\n    tags:\n      - 'v*'\njobs: {}\n",
    ".github/CODEOWNERS": "* @CapstoneTeam\n",
    ".github/PULL_REQUEST_TEMPLATE.md": "## Summary\n\n## Testing\n\n## Screenshots/Logs\n\n",

    # Hooks
    ".githooks/commit-msg": """#!/usr/bin/env bash
set -euo pipefail

msg_file="$1"
subject="$(head -n1 "$msg_file")"

# Example: feat(flutter): add vehicle mode toggle @anmol
pattern='^(feat|fix|perf|refactor|test|docs|style|chore|build|ci|revert)(\\([a-z0-9_-]+\\))?: .+ @[a-z0-9_]+$'

if ! [[ "$subject" =~ $pattern ]]; then
  echo "❌ Invalid commit message."
  echo "Use: type(scope): message @name"
  echo "Example: feat(flutter): add vehicle mode toggle @anmol"
  echo "Allowed types: feat fix perf refactor test docs style chore build ci revert"
  exit 1
fi
""",
    ".githooks/pre-commit": "#!/usr/bin/env bash\n# optional: run formatter/lint\nexit 0\n",
    ".githooks/pre-push": "#!/usr/bin/env bash\n# optional: quick test gate\nexit 0\n",

    # Docs
    "docs/architecture/overview.md": "# Architecture Overview\n",
    "docs/architecture/dataflow.md": "# Dataflow\n",
    "docs/architecture/interfaces.md": "# Interfaces\n",
    "docs/architecture/state_machines.md": "# State Machines\n",
    "docs/architecture/failure_modes.md": "# Failure Modes\n",
    "docs/architecture/threat_model.md": "# Threat Model\n",
    "docs/safety/estop.md": "# E-Stop\n",
    "docs/safety/safe_stop_policy.md": "# Safe Stop Policy\n",
    "docs/safety/override_policy.md": "# Override Policy\n",
    "docs/safety/privacy_policy.md": "# Privacy Policy\n",
    "docs/safety/retention_policy.md": "# Retention Policy\n",
    "docs/runbooks/onboarding.md": "# Onboarding\n",
    "docs/runbooks/local_dev.md": "# Local Development\n",
    "docs/runbooks/staging_deploy.md": "# Staging Deploy\n",
    "docs/runbooks/vehicle_bringup.md": "# Vehicle Bring-up\n",
    "docs/runbooks/incident_response.md": "# Incident Response\n",
    "docs/api/openapi.md": "# OpenAPI\n",
    "docs/api/websocket_events.md": "# Websocket Events\n",
    "docs/api/command_contracts.md": "# Command Contracts\n",

    # Schemas (placeholders)
    "schemas/README.md": "# Schemas\n\nSingle source of truth.\n",
    "schemas/openapi/openapi.yaml": "openapi: 3.0.3\ninfo:\n  title: ASV API\n  version: 0.1.0\npaths: {}\n",
    "schemas/proto/telemetry.proto": 'syntax = "proto3";\npackage asv;\n',
    "schemas/proto/commands.proto": 'syntax = "proto3";\npackage asv;\n',
    "schemas/proto/incidents.proto": 'syntax = "proto3";\npackage asv;\n',
    "schemas/proto/auth.proto": 'syntax = "proto3";\npackage asv;\n',
    "schemas/jsonschema/Telemetry.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "Telemetry",\n  "type": "object"\n}\n',
    "schemas/jsonschema/VehicleState.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "VehicleState",\n  "type": "object"\n}\n',
    "schemas/jsonschema/CommandRequest.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "CommandRequest",\n  "type": "object"\n}\n',
    "schemas/jsonschema/CommandResult.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "CommandResult",\n  "type": "object"\n}\n',
    "schemas/jsonschema/OverrideToken.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "OverrideToken",\n  "type": "object"\n}\n',
    "schemas/jsonschema/Incident.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "Incident",\n  "type": "object"\n}\n',
    "schemas/jsonschema/Alert.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "Alert",\n  "type": "object"\n}\n',
    "schemas/jsonschema/AuditEvent.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "AuditEvent",\n  "type": "object"\n}\n',
    "schemas/jsonschema/ConfigBundle.json": '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "title": "ConfigBundle",\n  "type": "object"\n}\n',

    # Infra (placeholders)
    "infra/codeserver/Dockerfile": "FROM codercom/code-server:latest\n",
    "infra/codeserver/docker-compose.yml": "version: '3.9'\nservices: {}\n",
    "infra/codeserver/entrypoint.sh": "#!/usr/bin/env bash\nset -e\nexec \"$@\"\n",
    "infra/codeserver/init-repo.sh": "#!/usr/bin/env bash\nset -e\n# clone repo / set hooks / install deps\n",
    "infra/codeserver/README.md": "# CodeServer\n",
    "infra/docker/vehicle.Dockerfile": "FROM ubuntu:24.04\n",
    "infra/docker/backend.Dockerfile": "FROM node:20\n",
    "infra/docker/sim.Dockerfile": "FROM ubuntu:24.04\n",
    "infra/docker/ml.Dockerfile": "FROM python:3.11\n",
    "infra/monitoring/prometheus.yml": "global:\n  scrape_interval: 15s\nscrape_configs: []\n",
    "infra/monitoring/grafana/README.md": "# Grafana configs\n",
    "infra/monitoring/dashboards/README.md": "# Dashboards\n",
    "infra/k8s/README.md": "# K8s manifests\n",
    "infra/k8s/namespaces/README.md": "# namespaces\n",
    "infra/k8s/backend/README.md": "# backend\n",
    "infra/k8s/monitoring/README.md": "# monitoring\n",
    "infra/k8s/ingress/README.md": "# ingress\n",
    "infra/terraform/README.md": "# Terraform\n",
    "infra/terraform/modules/README.md": "# modules\n",
    "infra/terraform/envs/README.md": "# envs\n",

    # Vehicle root
    "vehicle/README.md": "# Vehicle\n",
    "vehicle/config/vehicle.yaml": "vehicle:\n  name: asv\n",
    "vehicle/config/sensors.yaml": "sensors: {}\n",
    "vehicle/config/zones.yaml": "zones: []\n",
    "vehicle/config/rules.yaml": "rules: []\n",
    "vehicle/config/privacy.yaml": "privacy:\n  face_blur_default: true\n",
    "vehicle/config/logging.yaml": "logging:\n  level: INFO\n",
    "vehicle/config/model_manifest.yaml": "models: {}\n",
    "vehicle/launch/bringup.launch.py": "# bringup launch\n",
    "vehicle/launch/autonomy.launch.py": "# autonomy launch\n",
    "vehicle/launch/teleop.launch.py": "# teleop launch\n",
    "vehicle/launch/sim_bridge.launch.py": "# sim bridge launch\n",
    "vehicle/scripts/run_vehicle.sh": "#!/usr/bin/env bash\nset -e\n",
    "vehicle/scripts/record_bag.sh": "#!/usr/bin/env bash\nset -e\n",
    "vehicle/scripts/replay_bag.sh": "#!/usr/bin/env bash\nset -e\n",
    "vehicle/scripts/health_check.sh": "#!/usr/bin/env bash\nset -e\n",
    "vehicle/scripts/update_models.sh": "#!/usr/bin/env bash\nset -e\n",

    # Backend skeleton (placeholders)
    "backend/README.md": "# Backend\n",
    "backend/libs/common/config.ts": "export const config = {};\n",
    "backend/libs/common/logger.ts": "export const logger = console;\n",
    "backend/libs/common/errors.ts": "export class AppError extends Error {}\n",
    "backend/libs/common/validation.ts": "export const validate = () => true;\n",
    "backend/libs/schemas/README.md": "# Generated schema types\n",
    "backend/db/schema.sql": "-- schema\n",
    "backend/db/migrations/README.md": "# migrations\n",
    "backend/db/seed/README.md": "# seed\n",
}

# Create lots of empty service placeholders without manually typing 200 files.
SERVICE_NAMES = [
    "gateway", "auth", "fleet", "telemetry", "realtime", "commands", "approvals",
    "incidents", "alerting", "audit", "policy", "video", "config_rollout"
]
for svc in SERVICE_NAMES:
    REPO_STRUCTURE[f"backend/services/{svc}/src/README.md"] = f"# {svc}\n"
    REPO_STRUCTURE[f"backend/services/{svc}/tests/README.md"] = f"# tests for {svc}\n"

# Apps (Flutter) skeleton
REPO_STRUCTURE.update({
    "apps/operator_flutter/README.md": "# Operator Flutter App\n",
    "apps/operator_flutter/pubspec.yaml": "name: operator_flutter\nversion: 0.1.0\n",
    "apps/operator_flutter/analysis_options.yaml": "include: package:flutter_lints/flutter.yaml\n",
    "apps/operator_flutter/lib/main.dart": "void main() {}\n",
    "apps/operator_flutter/lib/app.dart": "// app entry\n",
    "apps/operator_flutter/lib/core/config.dart": "// config\n",
    "apps/operator_flutter/lib/core/auth/README.md": "# auth\n",
    "apps/operator_flutter/lib/core/networking/README.md": "# networking\n",
    "apps/operator_flutter/lib/core/realtime/README.md": "# realtime\n",
    "apps/operator_flutter/lib/core/storage/README.md": "# storage\n",
    "apps/operator_flutter/lib/core/logging/README.md": "# logging\n",
    "apps/operator_flutter/lib/models/README.md": "# models\n",
    "apps/operator_flutter/lib/shared_ui/README.md": "# shared UI\n",
})
FLUTTER_FEATURES = ["login", "vehicles", "live_map", "video", "incidents", "alerts", "controls", "approvals", "safety", "settings"]
for feat in FLUTTER_FEATURES:
    REPO_STRUCTURE[f"apps/operator_flutter/lib/features/{feat}/README.md"] = f"# {feat}\n"
REPO_STRUCTURE["apps/operator_flutter/test/README.md"] = "# tests\n"

# ML skeleton
REPO_STRUCTURE.update({
    "ml/README.md": "# ML\n",
    "ml/registry/manifests/README.md": "# manifests\n",
    "ml/registry/model_cards/README.md": "# model cards\n",
    "ml/registry/checksums/README.md": "# checksums\n",
    "ml/inference/runtimes/onnxruntime/README.md": "# onnxruntime runtime\n",
    "ml/inference/runtimes/tensorrt/README.md": "# tensorrt runtime\n",
    "ml/inference/postprocess/README.md": "# postprocess\n",
    "ml/inference/calibration/README.md": "# calibration\n",
    "ml/inference/bench/README.md": "# bench\n",
    "ml/training/pipelines/README.md": "# pipelines\n",
    "ml/training/configs/README.md": "# configs\n",
    "ml/training/augmentation/README.md": "# augmentation\n",
    "ml/training/evaluation/README.md": "# evaluation\n",
    "ml/training/exports/README.md": "# exports\n",
    "ml/data/raw/.gitkeep": "",
    "ml/data/interim/.gitkeep": "",
    "ml/data/processed/.gitkeep": "",
    "ml/data/labels/.gitkeep": "",
    "ml/data/datasheets/README.md": "# datasheets\n",
    "ml/tools/export_model.py": "# export model\n",
    "ml/tools/dataset_qc.py": "# dataset qc\n",
    "ml/tools/generate_model_card.py": "# model card generator\n",
})
ML_MODELS = ["object_detection", "behavior_detection", "alpr", "face_blur"]
for m in ML_MODELS:
    REPO_STRUCTURE[f"ml/models/{m}/README.md"] = f"# {m}\n"

# Simulation skeleton
REPO_STRUCTURE.update({
    "simulation/README.md": "# Simulation\n",
    "simulation/world/README.md": "# world\n",
    "simulation/vehicle_model/README.md": "# vehicle model\n",
    "simulation/sensors/README.md": "# sensors\n",
    "simulation/scenarios/intrusion.yaml": "scenario: intrusion\n",
    "simulation/scenarios/loitering.yaml": "scenario: loitering\n",
    "simulation/scenarios/tailing.yaml": "scenario: tailing\n",
    "simulation/scenarios/crowd_event.yaml": "scenario: crowd_event\n",
    "simulation/replay/align_timeline.py": "# align timeline\n",
    "simulation/replay/render_overlays.py": "# render overlays\n",
    "simulation/replay/export_report.py": "# export report\n",
    "simulation/evaluation/metrics.py": "# metrics\n",
    "simulation/evaluation/regressions.py": "# regressions\n",
    "simulation/evaluation/reports/README.md": "# reports\n",
})

# Tools skeleton
REPO_STRUCTURE.update({
    "tools/dev/setup-hooks.sh": "#!/usr/bin/env bash\nset -e\ngit config core.hooksPath .githooks\nchmod +x .githooks/commit-msg\n",
    "tools/dev/setup-codeserver.sh": "#!/usr/bin/env bash\nset -e\n# codeserver setup\n",
    "tools/dev/format.sh": "#!/usr/bin/env bash\nset -e\n# run formatters\n",
    "tools/dev/generate-clients.sh": "#!/usr/bin/env bash\nset -e\n# generate api clients\n",
    "tools/git/_commit_tag.sh": "#!/usr/bin/env bash\nset -e\n# commit helper\n",
    "tools/git/anmol": "#!/usr/bin/env bash\nset -e\nDIR=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\n\"$DIR/_commit_tag.sh\" anmol \"$@\"\n",
    "tools/git/jaspinder": "#!/usr/bin/env bash\nset -e\nDIR=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\n\"$DIR/_commit_tag.sh\" jaspinder \"$@\"\n",
    "tools/git/chris": "#!/usr/bin/env bash\nset -e\nDIR=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\n\"$DIR/_commit_tag.sh\" chris \"$@\"\n",
    "tools/git/prabh": "#!/usr/bin/env bash\nset -e\nDIR=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\n\"$DIR/_commit_tag.sh\" prabh \"$@\"\n",
    "tools/logs/parse.py": "# parse logs\n",
    "tools/logs/align.py": "# align logs\n",
    "tools/logs/export_incident_report.py": "# export incident report\n",
    "tools/logs/redact_video.py": "# redact video\n",
    "tools/calibration/README.md": "# calibration tools\n",
    "tools/dataset/README.md": "# dataset tools\n",
    "tools/labeling/README.md": "# labeling tools\n",
})

# Tests skeleton
REPO_STRUCTURE.update({
    "tests/contract/README.md": "# contract tests\n",
    "tests/integration/README.md": "# integration tests\n",
    "tests/sim/README.md": "# sim regression tests\n",
    "tests/e2e/README.md": "# end-to-end tests\n",
})


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str, overwrite: bool) -> None:
    ensure_parent_dir(path)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def chmod_executables(root: Path, relpaths: Iterable[str]) -> None:
    # Best effort: only on Unix-like systems.
    for rp in relpaths:
        p = root / rp
        if p.exists():
            try:
                p.chmod(0o755)
            except Exception:
                pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repo root folder to create, e.g. ./asv")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    # Create all files
    for rel, content in REPO_STRUCTURE.items():
        write_file(root / rel, content, overwrite=args.overwrite)

    # Mark shell scripts/hooks as executable
    executables = [
        ".githooks/commit-msg",
        ".githooks/pre-commit",
        ".githooks/pre-push",
        "vehicle/scripts/run_vehicle.sh",
        "vehicle/scripts/record_bag.sh",
        "vehicle/scripts/replay_bag.sh",
        "vehicle/scripts/health_check.sh",
        "vehicle/scripts/update_models.sh",
        "infra/codeserver/entrypoint.sh",
        "infra/codeserver/init-repo.sh",
        "tools/dev/setup-hooks.sh",
        "tools/dev/setup-codeserver.sh",
        "tools/dev/format.sh",
        "tools/dev/generate-clients.sh",
        "tools/git/_commit_tag.sh",
        "tools/git/anmol",
        "tools/git/jaspinder",
        "tools/git/chris",
        "tools/git/prabh",
    ]
    chmod_executables(root, executables)

    # Print a quick summary
    created_files = sum(1 for _ in REPO_STRUCTURE.keys())
    print(f"✅ Scaffold complete at: {root}")
    print(f"📄 Files listed in scaffold: {created_files}")
    print("Next:")
    print(f"  cd {root}")
    print("  git init")
    print("  ./tools/dev/setup-hooks.sh   # enforce commit style")


if __name__ == "__main__":
    main()
