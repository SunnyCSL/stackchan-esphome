#pragma once
#include <Arduino.h>
#include <driver/i2s.h>
#include <lwip/sockets.h>
#include <lwip/netdb.h>

static int udp_sock = -1;
static struct sockaddr_in udp_dest;
static volatile bool udp_active = false;
static i2s_port_t i2s_port = I2S_NUM_0;

void udp_stream_init(const char* host, uint16_t port) {
  udp_sock = lwip_socket(AF_INET, SOCK_DGRAM, 0);
  if (udp_sock < 0) return;
  
  memset(&udp_dest, 0, sizeof(udp_dest));
  udp_dest.sin_family = AF_INET;
  udp_dest.sin_port = htons(port);
  inet_aton(host, &udp_dest.sin_addr);
  
  // I2S already configured by ESPHome i2s_audio component on I2S_NUM_0
  ESP_LOGI("udp", "UDP stream init → %s:%d (I2S from ESPHome)", host, port);
}

void udp_stream_loop() {
  if (!udp_active || udp_sock < 0) return;
  
  uint8_t buf[640]; // 20ms @ 16kHz mono 16bit
  size_t bytes_read = 0;
  esp_err_t err = i2s_read(i2s_port, buf, 640, &bytes_read, 50 / portTICK_PERIOD_MS);
  
  if (err == ESP_OK && bytes_read > 0) {
    lwip_sendto(udp_sock, buf, bytes_read, 0,
                (struct sockaddr*)&udp_dest, sizeof(udp_dest));
  }
}

void udp_stream_start() {
  udp_active = true;
}

void udp_stream_stop() {
  udp_active = false;
}
