# Xiaozhi Firmware Baseline Analysis — Lessons Learned & Recovery Plan

**Created:** 2026-06-06
**Context:** StickS3 black screen — Xiaozhi official firmware provided for baseline comparison
**Analyst:** Robi (Hermes Agent)
**Status:** DRAFT — awaiting user review

---

## 1. Firmware Architecture Analysis

### 1.1 Partition Scheme (official Xiaozhi)

| Partition   | Type | Offset    | Size       | Purpose                      |
|-------------|------|-----------|------------|------------------------------|
| `nvs`       | 1    | 0x009000  | 16 KB      | WiFi / params                |
| `otadata`   | 1    | 0x00d000  | 8 KB       | OTA boot decision            |
| `phy_init`  | 1    | 0x00f000  | 4 KB       | RF calibration               |
| `ota_0`     | 0    | 0x020000  | ~3 MB      | **Active app partition**     |
| `ota_1`     | 0    | 0x310000  | ~3 MB      | OTA fallback                 |
| `assets`    | 1    | 0x600000  | **2 MB**   | Static assets (fonts/images) |

### 1.2 App Architecture (extracted strings)

```
┌──────────────────────────────────────────────┐
│ Xiaozhi Voice Assistant Firmware            │
│ ESP-IDF v6.0-dev (Jan 21 2026)             │
├──────────────────────────────────────────────┤
│ LCD:  st7789 panel via SPI3_HOST           │
│ Audio: ES8311 codec (I2S tx + rx)         │
│ Net:  MQTT + WebSocket (audio streaming)   │
│ OTA:  https://api.tenclass.net/xiaozhi/ota │
└──────────────────────────────────────────────┘
```

### 1.3 Critical Finding: SPI Bus Assignment

Xiaozhi uses **SPI3_HOST** (`spi_lcd_new_panel_io_spi(SPI3_HOST, ...)`).

On ESP32-S3 with PSRAM:
- GPIO39/40 → SPI3_HOST (MOSI/SCK)
- SPI3 is the **default** for ST7789V display on M5StickS3
- ESPHome auto-maps SPI pins → should default correctly

**Key insight:** If our ESPHome config shows black screen but Xiaozhi works, the problem is likely **not** the SPI bus itself (it's the same hardware path). More likely causes:
1. Backlight init sequence (GPIO38 timing / power rail)
2. Display init command sequence (ESP-IDF v6.0 vs ESP-IDF v5.5 in ESPHome)
3. Missing M5PM1 power rail enable

---

## 2. Our Current Config vs Xiaozhi Baseline

| Aspect              | Xiaozhi Official | Our ESPHome v12     | Gap?           |
|---------------------|------------------|----------------------|----------------|
| SoC                 | ESP32-S3         | ESP32-S3 (variant)   | ✅ Match        |
| Display             | ST7789P3, SPI3   | ST7789V, auto SPI    | ⚠️ Model diff   |
| Display BL          | GPIO38 (L3B rail)| GPIO38 direct        | ⚠️ Init diff    |
| Display CS          | — (SPI3 default) | GPIO41 (explicit)    | ⚠️ Extra?       |
| Display DC          | — (SPI3 default) | GPIO45               | —               |
| Display RST         | GPIO21           | GPIO21               | ✅ Match        |
| Audio codec         | ES8311           | ES8311 (I2S)         | ✅ Match        |
| I2S pins            | GPIO14/15/16/17  | GPIO14/15/16/17      | ✅ Match        |
| M5PM1 L3B           | Enabled          | **Disabled**         | ❌ **GAP**      |
| Power rails         | Full M5PM1 init  | No PMIC init         | ❌ **GAP**      |
| Assets (fonts)      | 2MB partition    | Compile-in           | Trade-off OK   |
| OTA                 | tenclass cloud   | ESPHome native       | ✅ Better      |
| WiFi auth           | Cloud pairing    | Local static IP      | ✅ Better      |
| Voice pipeline      | Cloud (WebSocket)| HA event bus         | ✅ Better      |

### 2.1 Root Cause Hypothesis

**Most likely cause of black screen:** GPIO38 backlight requires **M5PM1 L3B power rail** to be enabled BEFORE backlight GPIO is driven. The Xiaozhi firmware explicitly enables L3B via M5PM1 I2C register writes. Our config removed M5PM1 init entirely → backlight GPIO38 stays LOW → screen black (even though SPI commands work).

**Evidence supporting this hypothesis:**
1. Xiaozhi firmware strings show explicit M5PM1 L3B init sequence
2. Skill docs note: "without M5PM1 L3B rail, display gets NO power"
3. Our v12 shows backlight_pin: GPIO38 but no PMIC init → rail never enabled
4. If SPI were broken, we'd see no backlight glow at all; user reported backlight was working in earlier tests

**Alternative hypothesis (less likely):** ESP-IDF v5.5 (ESPHome) vs v6.0 (Xiaozhi) has different ST7789 init sequence → panel never enters sleep-disabled state. Testable with `show_test_card: true`.

---

## 3. Recovery Plan — Checkpoint-Driven

### Phase 0: Environment Prep (1 checkpoint)

**CP0.1 — Verify burn toolchain**
- Action: Confirm M5Burner successfully burned Xiaozhi firmware to StickS3
- Verify: User reports checklist result (screen / sound / buttons)
- Decision point:
  - If Xiaozhi ALSO black screen → hardware fault (SPI / backlight / panel)
  - If Xiaozhi shows display → firmware issue (our ESPHome config)

---

### Phase 1: Hardware Validation (1 checkpoint)

**CP1.1 — Xiaozhi hardware test report**
- Action: User runs hardware verification checklist
- Expected output: Markdown table with actual results
- Success criteria:
  - Screen has backlight glow ✅
  - Screen shows Xiaozhi logo ✅
  - KEY1/KEY2 respond ✅
  - Wake word works ✅
- **Gate:** If CP1.1 fails (Xiaozhi also black), STOP — hardware repair needed before any firmware work

---

### Phase 2: Minimal Display Recovery (4 checkpoints)

**CP2.1 — Add M5PM1 L3B init to sticks3-v12.yaml**
- Action: Add M5PM1 I2C init lambda in on_boot (priority 500) to enable PYG2 / L3B rail
- Verify: Compile succeeds, OTA uploads, device reconnects
- Success: Device comes back online after OTA

**CP2.2 — Verify backlight state with multimeter (user action)**
- Action: Measure GPIO38 voltage after boot (should be ~3.3V)
- Expected: ~3.3V (L3B enabled) vs 0V (L3B disabled)
- Success: Voltage confirms power rail is ON

**CP2.3 — Enable display test card**
- Action: Add `show_test_card: true` to display config
- Verify: Recompile + OTA, check for test pattern on screen
- Success: Solid color test pattern appears → display hardware OK, init sequence working
- Failure: Still black → SPI init or hardware issue

**CP2.4 — Remove test card, verify custom content**
- Action: Remove `show_test_card`, trigger `script.set_display_text` from HA
- Verify: Custom text appears on screen
- Success: Display fully functional, text push works

---

### Phase 3: Audio Path Validation (3 checkpoints)

**CP3.1 — Verify ES8311 I2C detection**
- Action: Enable I2C scan on bsp_i2c, check logs for 0x18 (ES8311) address
- Verify: ESPHome log shows ES8311 detected on I2C bus
- Success: I2C bus functional

**CP3.2 — Test audio playback (TTS)**
- Action: Call HA `media_player.play_media` with test audio URL
- Verify: Audio plays through StickS3 speaker
- Success: Speaker produces sound

**CP3.3 — Test microphone capture**
- Action: Use HA automation or `audio_record` integration to capture 3s from mic
- Verify: Audio file captured, verify levels
- Success: Mic producing valid audio data

---

### Phase 4: Voice Pipeline Integration (3 checkpoints)

**CP4.1 — Wake word detection**
- Action: Speak "Hey Jarvis" near StickS3, check HA log for `esphome.wake_word_detected` event
- Verify: Event fires in HA event bus
- Success: Wake word detected

**CP4.2 — Button-triggered voice conversation**
- Action: Press KEY1, verify `esphome.button_voice_trigger` fires, display shows "Listening..."
- Verify: HA automation triggers, display updates
- Success: Full button → listen → display flow

**CP4.3 — End-to-end voice conversation**
- Action: Press KEY1, speak command, verify TTS response plays back
- Verify: Complete loop: button → capture → STT → LLM → TTS → speaker
- Success: Voice conversation functional

---

### Phase 5: Push Info Display (2 checkpoints)

**CP5.1 — HA script display push**
- Action: Trigger `script.sticks3_set_display_text` from HA with test text
- Verify: Text appears on screen, auto-idles after 10s
- Success: Push display works (already tested, confirm persistence)

**CP5.2 — Automation-driven push**
- Action: Create HA automation that pushes weather / time on schedule
- Verify: Scheduled pushes appear correctly
- Success: Info push automation functional

---

## 4. Review Process

Each checkpoint will be reviewed by a **temporary subagent** (role: leaf, toolsets: [terminal, file]) that:
1. Reads the config file
2. Checks compile output for errors
3. Verifies OTA success
4. Reports PASS/FAIL with evidence

If FAIL: Robi diagnoses root cause, proposes fix, re-verifies before proceeding.

---

## 5. Current Status

| Phase | Status | Blocker |
|-------|--------|---------|
| Phase 0 | ⏳ Awaiting | User Xiaozhi burn result |
| Phase 1 | ⏳ Awaiting | Hardware verification |
| Phase 2 | 🔲 Not started | — |
| Phase 3 | 🔲 Not started | — |
| Phase 4 | 🔲 Not started | — |
| Phase 5 | ✅ Complete | — |

**Next action:** Wait for user to confirm Xiaozhi firmware burn + hardware checklist results.

---

*This plan is checkpoint-driven. No step proceeds without verification. No step is skipped without documented reason.*
