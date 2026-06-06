#!/usr/bin/env bash
# ==============================================================
# flash-stackchan.sh — USB flash recovery for StackChan CoreS3
#
# Usage:
#   ./flash-stackchan.sh                        # flash v13 firmware
#   ./flash-stackchan.sh /path/to/firmware.bin  # flash custom firmware
# ==============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR" && pwd)"

# ── Config ────────────────────────────────────────────────────
FIRMWARE="${1:-${PROJECT_DIR}/stackchan-v13/.pioenvs/stackchan/firmware.bin}"
FLASH_ADDR="0x0"
PING_TARGET="192.168.1.180"
PING_COUNT=3
PING_TIMEOUT=10

# ── Colors ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ── Check prerequisites ──────────────────────────────────────
check_prereqs() {
  local missing=()
  command -v esptool.py &>/dev/null || command -v esptool &>/dev/null || missing+=("esptool")
  command -v ping &>/dev/null || missing+=("ping")
  command -v lsblk &>/dev/null || true  # optional
  if [[ ${#missing[@]} -gt 0 ]]; then
    err "Missing required tools: ${missing[*]}"
    err "Install with: pip install esptool"
    exit 1
  fi
}

# ── Detect USB port ──────────────────────────────────────────
detect_port() {
  local port=""

  # Linux: /dev/ttyACM0 or /dev/ttyACM1
  if [[ "$(uname)" == "Linux" ]]; then
    for p in /dev/ttyACM0 /dev/ttyACM1; do
      if [[ -e "$p" ]]; then
        port="$p"
        break
      fi
    done
  # macOS: /dev/cu.usbmodem* or /dev/cu.usbserial*
  elif [[ "$(uname)" == "Darwin" ]]; then
    for p in /dev/cu.usbmodem* /dev/cu.usbserial*; do
      if [[ -e "$p" ]]; then
        port="$p"
        break
      done
  fi

  if [[ -z "$port" ]]; then
    err "No ESP32-S3 USB port found!"
    echo ""
    echo "  Linux:  /dev/ttyACM0 or /dev/ttyACM1"
    echo "  macOS:  /dev/cu.usbmodem* or /dev/cu.usbserial*"
    echo ""
    info "Make sure the device is connected via USB."
    info "On the CoreS3, you may need to hold the RESET button"
    info "while connecting, or press RESET twice quickly to"
    info "enter download mode."
    exit 1
  fi

  echo "$port"
}

# ── Flash firmware ───────────────────────────────────────────
flash_firmware() {
  local port="$1"
  local firmware="$2"

  if [[ ! -f "$firmware" ]]; then
    err "Firmware not found: $firmware"
    err "Compile first: esphome compile stackchan-v13.yaml"
    exit 1
  fi

  info "Flashing firmware to ${port} ..."
  info "Firmware: ${firmware} ($(du -h "$firmware" | cut -f1))"

  # Determine which esptool command to use
  local esptool_cmd
  if command -v esptool.py &>/dev/null; then
    esptool_cmd="esptool.py"
  else
    esptool_cmd="esptool"
  fi

  # Check if we need to specify --chip explicitly
  local chip_flag="--chip esp32s3"

  # ── Flash with verification ──
  if ! ${esptool_cmd} ${chip_flag} --port "${port}" --baud 921600 \
       write_flash --flash_mode dio --flash_size 16MB --flash_freq 80m \
       "${FLASH_ADDR}" "${firmware}"; then
    err "Flash failed! Trying lower baud rate..."
    sleep 1
    ${esptool_cmd} ${chip_flag} --port "${port}" --baud 115200 \
       write_flash --flash_mode dio --flash_size 16MB --flash_freq 80m \
       "${FLASH_ADDR}" "${firmware}"
  fi

  ok "Flash completed successfully!"
}

# ── Verify connectivity ──────────────────────────────────────
verify_connection() {
  local port="$1"

  info "Waiting for device to reboot (10s)..."
  sleep 10

  # Check port (old connection should drop, new one may appear)
  if [[ -e "$port" ]]; then
    ok "Port $port is still present (device reconnected)"
  else
    warn "Port $port disappeared (device may have rebooted to new firmware)"
  fi

  # Ping test
  info "Pinging ${PING_TARGET} (${PING_COUNT} tries, ${PING_TIMEOUT}s timeout)..."
  if ping -c "${PING_COUNT}" -W "${PING_TIMEOUT}" "${PING_TARGET}" &>/dev/null; then
    ok "Device is reachable at ${PING_TARGET}!"
    info "Try: curl http://${PING_TARGET}/"
    return 0
  else
    warn "Ping to ${PING_TARGET} failed after flash."
    warn "The device may still be booting, or the IP may differ."
    warn "Check your router's DHCP leases or use a serial monitor."
    return 1
  fi
}

# ── Print platform instructions ──────────────────────────────
print_instructions() {
  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "  StackChan CoreS3 — Flash Recovery Instructions"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
  echo "  LINUX:"
  echo "    Device:  /dev/ttyACM0 or /dev/ttyACM1"
  echo "    Perms:   sudo usermod -aG dialout \$USER  (then log out/in)"
  echo "    Build:   esphome compile stackchan-v13.yaml"
  echo "    Flash:   ./flash-stackchan.sh"
  echo ""
  echo "  macOS:"
  echo "    Device:  /dev/cu.usbmodem* or /dev/cu.usbserial*"
  echo "    Install: pip install esptool"
  echo "    Build:   esphome compile stackchan-v13.yaml"
  echo "    Flash:   ./flash-stackchan.sh"
  echo ""
  echo "  ENTERING DOWNLOAD MODE (CoreS3):"
  echo "    1. Hold the RESET button"
  echo "    2. While holding, connect USB"
  echo "    3. Release RESET"
  echo "    OR: Double-press RESET quickly"
  echo ""
  echo "  SAFE MODE (triple-press reset after flash):"
  echo "    Triple-press the RESET button → enters safe mode"
  echo "    with OTA available for wireless recovery."
  echo ""
  echo "  POST-FLASH:"
  echo "    curl http://${PING_TARGET}/   (web_server health check)"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
}

# ── Main ──────────────────────────────────────────────────────
main() {
  echo ""
  echo "╔══════════════════════════════════════════════╗"
  echo "║   StackChan CoreS3 — USB Flash Recovery      ║"
  echo "╚══════════════════════════════════════════════╝"
  echo ""

  check_prereqs

  local port
  port="$(detect_port)"
  ok "Found device at ${port}"

  flash_firmware "$port" "$FIRMWARE"

  verify_connection "$port" || true

  print_instructions
}

main "$@"
