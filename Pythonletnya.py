import flet as ft
import serial
import threading
import re
class SerialReader(threading.Thread):
    def __init__(self, port, baudrate, callback):
        super().__init__()
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.callback = callback
        self._running = True
        self.buffer = ""
    def run(self):
        while self._running:
            if self.serial_port.in_waiting > 0:
                try:
                    line = self.serial_port.readline().decode("utf-8").strip()
                    print(f"[Serial]: {line}")
                    self.buffer += line + "\n"
                    if "READY" in line:
                        self.callback(self.buffer)
                        self.buffer = ""
                except UnicodeDecodeError:
                    continue
    def stop(self):
        self._running = False
        if self.serial_port.is_open:
            self.serial_port.close()
    def send_command(self, command):
        if self.serial_port.is_open:
            self.serial_port.write((command + "\n").encode("utf-8"))
            print(f"[Python]: Отправлена команда: {command}")
def main(page: ft.Page):
    page.title = "Игра на реакцию"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 420
    page.window_height = 580
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    # Заголовок
    title = ft.Text("Игра на реакцию", size=32, weight="bold", text_align="center")
    attempt_input = ft.TextField(
        label="Введите количество попыток (3–10)",
        width=250,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        border_color="blue",
    )
    # Статус
    status = ft.Text("Готов к запуску", size=16, color="blue", text_align="center")
    # Кнопка запуска
    def start_game(e):
        result_column.visible = False
        status.value = ""
        status.color = "blue"
        page.update()
        try:
            attempts = int(attempt_input.value)
            if 3 <= attempts <= 10: 
                serial_thread.send_command(str(attempts)
                serial_thread.send_command("START")        
                status.value = f"Игра запущена с {attempts} попытками..."
                start_btn.disabled = True
                page.update()
            else:
                status.value = "Введите число от 3 до 10."
                status.color = "red"
                page.update()
        except ValueError:
            status.value = "Ошибка: введите корректное число."
            status.color = "red"
            page.update()

    start_btn = ft.ElevatedButton(
        "Начать игру",
        on_click=start_game,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
    )
    # Тексты результатов
    hits = ft.Text("", size=20)
    errors = ft.Text("", size=20)
    bestreakt = ft.Text("", size=20)
    medreakt = ft.Text("", size=20)
    result_column = ft.Column(
        [hits, errors, bestreakt, medreakt],
        visible=False,
        spacing=10,
    )
    # Обработка результата от Arduino
    def parse_result(text):
        hit_match = re.search(r"Hits\s*-\s*(\d+)", text)
        err_match = re.search(r"Errors\s*-\s*(\d+)", text)
        best_match = re.search(r"Bestreakt\s*-\s*(\d+)", text)
        med_match = re.search(r"Medreakt\s*-\s*(\d+)", text)
        hits.value = f"✅ Попаданий: {hit_match.group(1) if hit_match else '0'}"
        errors.value = f"❌ Ошибок: {err_match.group(1) if err_match else '0'}"
        bestreakt.value = f"⚡ Лучшая реакция: {best_match.group(1) if best_match else '0'} мс"
        medreakt.value = f"📊 Средняя реакция: {med_match.group(1) if med_match else '0'} мс"
status.value = "Результаты получены!"
        status.color = "green"
        result_column.visible = True
        start_btn.disabled = False
        page.update()
    # Сборка страницы
    page.add(ft.Container(
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
                spacing=25,
            ),
            alignment=ft.Alignment(0,0),
            padding=20,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=4,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(4, 4),
            )
        )
    )
    try:
        port = "/dev/cu.usbserial-140"  
        global serial_thread
        serial_thread = SerialReader(port, 9600, parse_result)
        serial_thread.start()
    except serial.SerialException as e:
        status.value = f"Ошибка подключения: {e}"
        status.color = "red"
        start_btn.disabled = True
        page.update()
    def on_close(e):
        if 'serial_thread' in globals():
            serial_thread.stop()
    page.on_window_close = on_close
if __name__ == "__main__":
    ft.app(target=main)
