import flet as ft
import serial
import serial.tools.list_ports
import threading
import re

class SerialReader(threading.Thread):
    def __init__(self, port, baudrate, callback):
        super().__init__()
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
        except Exception as e:
            print(f"Ошибка открытия порта: {e}")
            self.serial_port = None
        
        self.callback = callback
        self._running = True
        self.buffer = ""

    def run(self):
        while self._running and self.serial_port:
            if self.serial_port.in_waiting > 0:
                try:
                    line = self.serial_port.readline().decode("utf-8").strip()
                    print(f"[Serial]: {line}")
                    self.buffer += line + "\n"
                    # Если Arduino прислала READY, значит пакет данных окончен
                    if "READY" in line:
                        self.callback(self.buffer)
                        self.buffer = ""
                except UnicodeDecodeError:
                    continue

    def stop(self):
        self._running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def send_command(self, command):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write((command + "\n").encode("utf-8"))
            print(f"[Python]: Отправлена команда: {command}")

def main(page: ft.Page):
    page.title = "Игра на реакцию"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 420
    page.window_height = 650
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    # Элементы интерфейса
    title = ft.Text("Игра на реакцию", size=32, weight="bold", text_align="center")
    
    attempt_input = ft.TextField(
        label="Попыток (3–10)",
        value="5",
        width=250,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        border_color="blue",
    )

    status = ft.Text("Поиск Arduino...", size=16, color="blue", text_align="center")

    hits = ft.Text("", size=18, weight="w500")
    errors = ft.Text("", size=18, weight="w500")
    bestreakt = ft.Text("", size=18, weight="w500")
    medreakt = ft.Text("", size=18, weight="w500")

    result_column = ft.Column(
        [hits, errors, bestreakt, medreakt],
        visible=False,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    def parse_result(text):
        # Поиск данных в тексте с помощью регулярных выражений
        hit_match = re.search(r"Hits\s*-\s*(\d+)", text)
        err_match = re.search(r"Errors\s*-\s*(\d+)", text)
        best_match = re.search(r"Bestreakt\s*-\s*(\d+)", text)
        med_match = re.search(r"Medreakt\s*-\s*(\d+)", text)

        hits.value = f"✅ Попаданий: {hit_match.group(1) if hit_match else '0'}"
        errors.value = f"❌ Ошибок: {err_match.group(1) if err_match else '0'}"
        bestreakt.value = f"⚡ Лучшая: {best_match.group(1) if best_match else '0'} мс"
        medreakt.value = f"📊 Средняя: {med_match.group(1) if med_match else '0'} мс"

        status.value = "Результаты получены!"
        status.color = "green"
        result_column.visible = True
        start_btn.disabled = False
        page.update()

    def start_game(e):
        result_column.visible = False
        try:
            attempts = int(attempt_input.value)
            if 3 <= attempts <= 10:
                # Отправляем количество попыток, затем команду START
                serial_thread.send_command(str(attempts))
                serial_thread.send_command("START")
                
                status.value = f"Игра началась! Попыток: {attempts}"
                status.color = "orange"
                start_btn.disabled = True
                page.update()
            else:
                status.value = "Введите от 3 до 10!"
                status.color = "red"
                page.update()
        except ValueError:
            status.value = "Ошибка: введите число."
            status.color = "red"
            page.update()

    start_btn = ft.ElevatedButton(
        "Начать игру",
        on_click=start_game,
        disabled=True,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
    )

    # Сборка интерфейса в карточку
    card = ft.Container(
        content=ft.Column(
            [
                title,
                attempt_input,
                start_btn,
                status,
                result_column,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        padding=30,
        border_radius=15,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLUE_GREY_100)
    )

    page.add(card)

    # Поиск порта Arduino
    ports = list(serial.tools.list_ports.comports())
    arduino_port = None
    for p in ports:
        # Ищем типичные названия для Arduino или ваш порт
        if "usb" in p.device.lower() or "COM" in p.device:
            arduino_port = p.device
            break

    if arduino_port:
        global serial_thread
        serial_thread = SerialReader(arduino_port, 9600, parse_result)
        serial_thread.start()
        status.value = f"Подключено: {arduino_port}"
        status.color = "green"
        start_btn.disabled = False
    else:
        status.value = "Arduino не найдена!"
        status.color = "red"

    def on_close(e):
        if 'serial_thread' in globals():
            serial_thread.stop()

    page.on_window_close = on_close
    page.update()

if __name__ == "__main__":
    # Вместо ft.app(target=main) используем актуальный метод
    ft.run(main)
