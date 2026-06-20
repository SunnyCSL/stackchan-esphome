#!/bin/bash
# Extract HA iOS refresh token to a radxa-readable file
# Run once with sudo, or whenever HA regenerates tokens
echo "Extracting HA iOS refresh token..."
sudo python3 -c "
import json
with open('/home/radxa/homeassistant/.storage/auth') as f:
    data = json.load(f)
for t in data['data']['refresh_tokens']:
    if t.get('client_id') == 'https://home-assistant.io/iOS':
        with open('/home/radxa/stackchan-esphome/xvf3800/.ha_ios_token', 'w') as out:
            out.write(t['token'])
        print('Token extracted OK')
        break
"
sudo chown radxa:radxa /home/radxa/stackchan-esphome/xvf3800/.ha_ios_token
chmod 600 /home/radxa/stackchan-esphome/xvf3800/.ha_ios_token
echo "Done. Token file: /home/radxa/stackchan-esphome/xvf3800/.ha_ios_token"
