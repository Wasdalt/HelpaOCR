#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Ошибка: Пожалуйста, запустите с помощью sudo"
  exit 1
fi

# Путь установки приложения
INSTALL_PATH="/opt/HelpaOCR"

# Переходим в папку, где находится install.sh
cd "$(dirname "$0")"

# Удаление существующей папки установки, если она уже существует
if [ -d "$INSTALL_PATH" ]; then
  echo "Удаление установленного HelpaOCR..."
  rm -rf "$INSTALL_PATH"
  echo -e "\033[32mУдалено!\033[0m"
fi

# Создание папки установки
echo "Создание установочного каталога..."
mkdir -p "$INSTALL_PATH"
echo -e "\033[32mСделано!\033[0m"

# Распаковка приложения в путь установки
echo "Установка HelpaOCR..."
cp -r ./* "$INSTALL_PATH"
echo -e "\033[32mДалее...\033[0m"

# Установка прав доступа для файлов и папок внутри /opt/HelpaOCR
chmod -R 755 "$INSTALL_PATH"

# Удаление существующей символической ссылки, если она уже существует
if [ -L "/usr/local/bin/HelpaOCR" ]; then
  echo "Удаление зависимостей..."
  rm "/usr/local/bin/HelpaOCR"
  echo -e "\033[32mУдалено!\033[0m"
fi

# Создание символической ссылки на исполняемый файл в /opt/HelpaOCR
ln -s "$INSTALL_PATH/HelpaOCR" "/usr/local/bin/HelpaOCR"

# Добавление пути к приложению в переменную окружения PATH
echo "export PATH=\$PATH:$INSTALL_PATH" >> ~/.bashrc
echo "export PATH=\$PATH:$INSTALL_PATH" >> ~/.bash_profile
source ~/.bashrc
source ~/.bash_profile

# Создание .desktop файла с правами на чтение и запись для всех пользователей
echo "Создание ярлыка..."
cat > /usr/share/applications/HelpaOCR.desktop << EOL
[Desktop Entry]
Name=Helpa OCR
Exec=/usr/local/bin/HelpaOCR
Icon=$INSTALL_PATH/icon/icon.png
Terminal=false
Type=Application
Categories=Utility;
EOL

# Установка прав на чтение и запись для всех пользователей
chmod a+rw /usr/share/applications/HelpaOCR.desktop
echo -e "\033[32mСделано!\033[0m"

# Удаление символической ссылки на uninstall-HelpaOCR.sh, если она существует
if [ -L "/usr/local/bin/uninstall-HelpaOCR" ]; then
  echo "Удаление зависимостей..."
  rm "/usr/local/bin/uninstall-HelpaOCR"
  echo -e "\033[32mУдалено!\033[0m"
fi

# Создание символической ссылки на uninstall-HelpaOCR.sh
ln -s "$INSTALL_PATH/uninstall-HelpaOCR.sh" "/usr/local/bin/uninstall-HelpaOCR"

# Обновление базы данных .desktop
echo "Обновление базы данной..."
update-desktop-database
echo -e "\033[32mСделано!\033[0m"
