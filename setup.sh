#!/bin/bash
cp eviction-notify.service /etc/systemd/system/eviction-notify.service
cp eviction_notify.py /opt

systemctl enable eviction-notify
systemctl start eviction-notify
