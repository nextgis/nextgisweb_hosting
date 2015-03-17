/etc/openvpn/tap_client.conf:
  file.managed:
    - source: salt://openvpn_tap_client/tap_client.conf

/etc/openvpn/tap_client_control.sh:
  file.managed:
    - source: salt://openvpn_tap_client/tap_client_control.sh
    - mode: 750

/etc/network/interfaces.d/tap0.cfg:
  file.managed:
    - source: salt://openvpn_tap_client/network/interfaces.d/tap0.cfg

openvpn:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - require:
      - file: /etc/openvpn/tap_client.conf
      - file: /etc/openvpn/tap_client_control.sh
    - watch:
      - file: /etc/openvpn/tap_client.conf
      - file: /etc/openvpn/tap_client_control.sh


resolvconf:
  pkg.installed
