#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Ошибка: Пожалуйста, запустите с помощью sudo"
  exit 1
fi

INSTALL_PATH="/opt/HelpaOCR"

cd "$INSTALL_PATH"

if [ -L "/usr/local/bin/HelpaOCR" ]; then
  rm "/usr/local/bin/HelpaOCR"
fi

if [ -f "/usr/share/applications/HelpaOCR.desktop" ]; then
  rm "/usr/share/applications/HelpaOCR.desktop"
fi

update-desktop-database

if [ -L "/usr/local/bin/uninstall-HelpaOCR" ]; then
  rm "/usr/local/bin/uninstall-HelpaOCR"
fi

rm -rf "$INSTALL_PATH"
echo "Удалено!"
