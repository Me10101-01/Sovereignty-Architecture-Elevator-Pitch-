#!/usr/bin/env bash
set -euo pipefail

ADOPTIUM_API="https://api.adoptium.net/v3"
SUPPORTED_VERSIONS="11 17 21 25"
INSTALL_DIR="${HOME}/.local/jdks"
BIN_DIR="${HOME}/.local/bin"

detect_os_arch() {
  OS=$(uname -s | tr '[:upper:]' '[:lower:]')
  ARCH=$(uname -m)
  case "$ARCH" in
    x86_64) ARCH="x64" ;;
    aarch64|arm64) ARCH="aarch64" ;;
    *) echo "Unsupported arch: $ARCH" && exit 1 ;;
  esac
  case "$OS" in
    darwin) OS="mac" ;;
    linux) OS="linux" ;;
    *) echo "Unsupported OS: $OS" && exit 1 ;;
  esac
}

download_and_install() {
  local version=$1
  local json=$(curl -s "${ADOPTIUM_API}/assets/latest/${version}/hotspot?release=latest&jvm_impl=hotspot&heap_size=normal&os=${OS}&arch=${ARCH}&image_type=jdk&project=jdk&vendor=eclipse")
  local url=$(echo "$json" | jq -r '.[0].binary.package.link')
  local name=$(echo "$json" | jq -r '.[0].binary.package.name')
  local dir="${INSTALL_DIR}/jdk-${version}"

  echo "Downloading OpenJDK ${version} from Adoptium..."
  mkdir -p "$dir"
  curl -L "$url" | tar -xz -C "$dir" --strip-components=1
  echo "Installed to $dir"
}

verify_jdk() {
  local java_bin=$1/bin/java
  "$java_bin" --version
  echo "public class Test { public static void main(String[] args) { System.out.println(\"Hello CloudOS JDK ${version}\"); } }" > /tmp/Test.java
  "$java_bin" /tmp/Test.java && echo "✓ Compilation + execution test passed"
  rm /tmp/Test.java
}

install() {
  local version=$1
  if [[ ! " $SUPPORTED_VERSIONS " =~ " $version " ]]; then
    echo "Supported versions: $SUPPORTED_VERSIONS"
    exit 1
  fi
  detect_os_arch
  mkdir -p "$INSTALL_DIR"
  download_and_install "$version"
  verify_jdk "${INSTALL_DIR}/jdk-${version}"
}

use() {
  local version=$1
  local jdk_path="${INSTALL_DIR}/jdk-${version}"
  if [[ ! -d "$jdk_path" ]]; then
    echo "JDK $version not installed. Run: $0 install $version"
    exit 1
  fi
  mkdir -p "$BIN_DIR"
  ln -sf "${jdk_path}/bin/"* "$BIN_DIR"/
  echo "Switched to OpenJDK $version"
  java --version
}

case "${1:-}" in
  install) install "$2" ;;
  use) use "$2" ;;
  list) ls -1 "$INSTALL_DIR" ;;
  *) echo "Usage: $0 install|use|list <version>" ;;
esac
