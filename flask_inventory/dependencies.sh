#!/bin/bash

# ↓pipが未導入ならインストールするのよ。↓
# sudo dnf install python3.12-pip -y

# 標準ライブラリに含まれてないやつだけ載せておくわ。
python3.12 -m pip install Flask qrcode pillow chardet reportlab
