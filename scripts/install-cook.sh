#!/usr/bin/env bash
set -euo pipefail
# Pinned official Linux x86_64 binary; verify before extracting or running.
cd "$(dirname "$0")/.."
mkdir -p .tools
archive=$(mktemp)
trap 'rm -f "$archive"' EXIT
curl --fail --location --silent --show-error \
  https://github.com/cooklang/cookcli/releases/download/v0.41.1/cook-0.41.1-linux-x86_64-musl.tar.gz \
  --output "$archive"
echo "342378f8121ba8b12cb13654119348860001bb3ab07ca00ba65f59ad00b51354  $archive" | sha256sum --check --status
tar -xzf "$archive" -C .tools cook
.tools/cook --version
