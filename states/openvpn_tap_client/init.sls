/etc/openvpn/tap_client.conf:
  file.managed:
    - source: salt://openvpn_tap_client/tap_client.conf

/etc/openvpn/tap_client_up.sh:
  file.managed:
    - source: salt://openvpn_tap_client/tap_client_up.sh
    - mode: 740

/etc/openvpn/tap_client_down.sh:
  file.managed:
    - source: salt://openvpn_tap_client/tap_client_down.sh
    - mode: 740

openvpn:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - require:
      - file: /etc/openvpn/tap_client.conf
      - file: /etc/openvpn/tap_client_up.sh
      - file: /etc/openvpn/tap_client_down.sh
    - watch:
      - file: /etc/openvpn/tap_client.conf
      - file: /etc/openvpn/tap_client_up.sh
      - file: /etc/openvpn/tap_client_down.sh


resolvconf:
  pkg.installed
