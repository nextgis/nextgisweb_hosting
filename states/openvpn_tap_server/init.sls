/etc/openvpn/tap_server.conf:
  file.managed:
    - source: salt://openvpn_tap_server/tap_server.conf

/etc/openvpn/tap_server_up.sh:
  file.managed:
    - source: salt://openvpn_tap_server/tap_server_up.sh
    - mode: 740

/etc/openvpn/tap_server_down.sh:
  file.managed:
    - source: salt://openvpn_tap_server/tap_server_down.sh
    - mode: 740

openvpn:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - require:
      - file: /etc/openvpn/tap_server.conf
      - file: /etc/openvpn/tap_server_up.sh
      - file: /etc/openvpn/tap_server_down.sh
    - watch:
      - file: /etc/openvpn/tap_server.conf
      - file: /etc/openvpn/tap_server_up.sh
      - file: /etc/openvpn/tap_server_down.sh


resolvconf:
  pkg.installed
