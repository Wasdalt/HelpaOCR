import fcntl
import subprocess
import sys
import pytesseract
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QDialog, QHBoxLayout, \
    QMessageBox, QDesktopWidget
from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QCursor
from PyQt5.QtCore import Qt, QTimer, QRect, QBuffer
from io import BytesIO
import os


def check_package_installed(package_name):
    package_managers = ["apt", "yum", "dnf", "pacman"]

    for package_manager in package_managers:
        try:
            if package_manager == "pacman":
                subprocess.check_call([package_manager, "-Q", package_name], stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            else:
                subprocess.check_call([package_manager, "list", package_name], stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            continue
        except subprocess.CalledProcessError:
            return False

    return False

class MyApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon", "icon.png")))


class OutputDialog(QDialog):
    def __init__(self, text):
        super().__init__()
        self.setWindowTitle("Распознанный текст")
        dialog_layout = QVBoxLayout()

        # Create QTextEdit and hide the scrollbars
        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        dialog_layout.addWidget(text_edit)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_and_copy_text)  # Connect the custom slot
        button_layout.addStretch(1)  # Add stretchable space to the left
        button_layout.addWidget(ok_button)

        dialog_layout.addLayout(button_layout)  # Add the button layout to the main layout
        self.setLayout(dialog_layout)

        # Set focus on the OK button
        ok_button.setFocus()

    def accept_and_copy_text(self):
        clipboard = QApplication.clipboard()
        text_edit = self.findChild(QTextEdit)
        clipboard.setText(text_edit.toPlainText())
        self.accept()  # Accept the dialog to close it


class FullscreenDimmer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.activate_timer = QTimer(self)
        self.activate_timer.timeout.connect(self.activate_window)
        self.selection_rect = None
        self.start_pos = None
        self.screenshot_pixmap = None

    def closeEvent(self, event):
        # При закрытии этого окна, закрываем все окна приложения
        QApplication.closeAllWindows()
        event.accept()  # Принимаем событие закрытия

    def init_ui(self):
        self.setWindowTitle('Helpa OCR')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Окно поверх всех окон
        self.setStyleSheet("background-color: black;")  # Задаем черный фон окна
        self.setWindowOpacity(0.25)  # Устанавливаем полупрозрачность окна (от 0.0 до 1.0)

    def activate_window(self):
        self.activateWindow()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.selection_rect = None

    def mouseMoveEvent(self, event):
        if self.start_pos:
            end_pos = event.pos()
            self.selection_rect = QRect(
                min(self.start_pos.x(), end_pos.x()),
                min(self.start_pos.y(), end_pos.y()),
                abs(self.start_pos.x() - end_pos.x()),
                abs(self.start_pos.y() - end_pos.y())
            )
            self.update()

    def paintEvent(self, event):
        if self.selection_rect:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 0, 0)))  # Убираем альфа-канал для контура
            painter.setBrush(QBrush(QColor(255, 255, 255, 30)))  # Задаем кисть для заливки
            painter.drawRect(self.selection_rect)

            # Добавляем контрастный контур
            contrast_pen = QPen(QColor(255, 0, 0, 200), 1)  # Белый с прозрачностью 200 и толщиной 2
            painter.setPen(contrast_pen)
            painter.drawRect(self.selection_rect)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos:
            end_pos = event.pos()
            self.selection_rect = QRect(
                min(self.start_pos.x(), end_pos.x()),
                min(self.start_pos.y(), end_pos.y()),
                abs(self.start_pos.x() - end_pos.x()),
                abs(self.start_pos.y() - end_pos.y())
            )
            self.update()
            self.start_pos = None
            self.perform_ocr()

    def perform_ocr(self):
        if self.selection_rect:
            current_screen = QApplication.desktop().screenNumber(self)

            # Get the window id of the current widget
            window_id = self.winId()

            screenshot = QApplication.primaryScreen().grabWindow(
                window_id,
                self.selection_rect.x(), self.selection_rect.y(),
                self.selection_rect.width(), self.selection_rect.height()
            )
            self.screenshot_pixmap = screenshot

            # Output the size of the selection to the console
            # print(f"Selection Size: Width = {self.selection_rect.width()}, Height = {self.selection_rect.height()}")

            # Convert the QPixmap to a PIL Image object
            qimage = self.screenshot_pixmap.toImage()
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            qimage.save(buffer, "png")
            pil_image = Image.open(BytesIO(buffer.data()))

            # # Save the screenshot to the project directory
            # project_path = os.path.dirname(os.path.realpath(__file__))
            # screenshot_filename = os.path.join(project_path, "screenshot.png")
            # pil_image.save(screenshot_filename)

            # Perform OCR using pytesseract with custom configuration
            custom_config = r'--oem 3 --psm 6'
            recognized_text = pytesseract.image_to_string(pil_image, lang='eng+rus', config=custom_config)

            # Открыть новое окно для вывода текста
            self.show_text_dialog(recognized_text)

            # Очищаем QPixmap после использования
            self.screenshot_pixmap = None

            # Clear the selection rectangle
            self.clear_selection()

    def clear_selection(self):
        self.selection_rect = None
        self.update()

    def show_text_dialog(self, text):
        dialog = OutputDialog(text)
        dialog.exec_()


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def install_missing_packages():
    script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "install_pag.sh")
    try:
        subprocess.run(["pkexec", "bash", script_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print("Ошибка при установке пакетов:", e)
        return False

LOCKFILE = "/tmp/my_program_lockfile.lock"

def acquire_lock():
    try:
        # Создаем виртуальный файловый дескриптор
        lock_fd = open(LOCKFILE, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_fd
    except OSError:
        print("Программа уже запущена.")
        sys.exit(1)

def release_lock(lock_fd):
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()

def main():
    lock_fd = acquire_lock()
    app = MyApp(sys.argv)

    # Проверяем наличие необходимых пакетов перед запуском приложения
    required_packages = ["tesseract", "tesseract-data-eng", "tesseract-data-rus"]
    missing_packages = [pkg for pkg in required_packages if not check_package_installed(pkg)]

    if missing_packages:
        message = f"Необходимо установить недостающие пакеты для работы приложения"

        # Создаем кастомное окно сообщения с кнопками "Назад" и "Установить"
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Отсутствующие пакеты")
        msg_box.setText(message)
        msg_box.addButton("Назад", QMessageBox.RejectRole)
        msg_box.addButton("Установить", QMessageBox.AcceptRole)

        # Показываем окно и ждем ответа
        response = msg_box.exec_()
        if response == QMessageBox.Rejected:
            release_lock(lock_fd)  # Освобождаем блокировку перед завершением
            return
        elif response == QMessageBox.Accepted:
            if install_missing_packages():
                # Если установка прошла успешно, перезапускаем программу
                release_lock(lock_fd)  # Освобождаем блокировку перед перезапуском
                restart_program()
                return
            else:
                # Обработка ошибки установки
                release_lock(lock_fd)  # Освобождаем блокировку перед завершением
                return

    for screen in app.screens():
        dimmer = FullscreenDimmer()
        dimmer.setGeometry(screen.geometry())
        dimmer.showFullScreen()

    main_screen_dimmer = FullscreenDimmer()
    main_screen_dimmer.showFullScreen()

    # Обработка событий приложения
    ret_code = app.exec_()
    release_lock(lock_fd)  # Освобождаем блокировку
    sys.exit(ret_code)  #


if __name__ == '__main__':
    main()