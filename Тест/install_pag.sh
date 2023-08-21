#!/bin/bash

print_error() {
    local RED='\033[0;31m'
    local NC='\033[0m'
    echo -e "${RED}$1${NC}"
}

if ping -q -c 1 8.8.8.8 &>/dev/null; then
    echo "Интернет подключение доступно. Продолжаем установку пакетов."
else
    print_error "Ошибка: Нет доступа к интернету. Установка пакетов невозможна."
    exit 1
fi

if command -v apt-get &>/dev/null; then
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-rus
    exit 0
fi

if command -v dnf &>/dev/null; then
    sudo dnf install -y tesseract tesseract-langpack-eng tesseract-langpack-rus
    exit 0
fi

if command -v yum &>/dev/null; then
    sudo yum install -y tesseract tesseract-langpack-eng tesseract-langpack-rus
    exit 0
fi

if command -v pacman &>/dev/null; then
    sudo pacman -S --noconfirm tesseract tesseract-data-eng tesseract-data-rus
    exit 0
fi
