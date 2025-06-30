import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, time
import threading
import json
import os
from pygame import mixer
import time as tm


class WakeUpScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Умный будильник для студентов")
        self.root.geometry("600x500")

        # Инициализация микшера pygame
        mixer.init()

        # Настройки по умолчанию
        self.settings_file = "alarm_settings.json"
        self.default_sound = "alarm.wav"  # Можно добавить файл по умолчанию

        self.wake_up_times = {'Числитель': {}, 'Знаменатель': {}}
        self.current_week_type = self.detect_week_type()
        self.alarm_sound_path = None
        self.alarm_thread = None
        self.running = True

        # Загрузка сохраненных настроек
        self.load_settings()

        self.create_widgets()
        self.start_alarm_checker()

        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def detect_week_type(self):
        """Определяет числитель или знаменатель по текущей неделе"""
        week_number = datetime.now().isocalendar()[1]
        return 'Числитель' if week_number % 2 == 1 else 'Знаменатель'

    def create_widgets(self):
        """Создает все элементы интерфейса"""
        # Стилизация
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

        # Главный контейнер
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Верхняя панель с информацией
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            self.header_frame,
            text=f"Текущая неделя: {self.current_week_type}",
            style='Header.TLabel'
        ).pack(side=tk.LEFT)

        # Кнопки управления
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            self.control_frame,
            text="Редактировать расписание",
            command=self.show_schedule_editor
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.control_frame,
            text="Выбрать мелодию",
            command=self.choose_sound
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self.control_frame,
            text="Экспорт в CSV",
            command=self.export_to_csv
        ).pack(side=tk.RIGHT, padx=5)

        # Отображение текущего расписания
        self.schedule_frame = ttk.Frame(self.main_frame)
        self.schedule_frame.pack(fill=tk.BOTH, expand=True)

        self.display_current_schedule()

        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        ).pack(fill=tk.X, pady=(10, 0))

    def display_current_schedule(self):
        """Отображает текущее расписание"""
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

        # Таблица расписания
        columns = ("День недели", "Время пробуждения")
        self.schedule_tree = ttk.Treeview(
            self.schedule_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        for col in columns:
            self.schedule_tree.heading(col, text=col)
            self.schedule_tree.column(col, width=150, anchor=tk.CENTER)

        self.schedule_tree.pack(fill=tk.BOTH, expand=True)

        # Заполнение данными
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        for day in days:
            wake_time = self.wake_up_times[self.current_week_type].get(day, None)
            time_str = wake_time.strftime("%H:%M") if isinstance(wake_time, time) else "Не установлено"
            self.schedule_tree.insert("", tk.END, values=(day, time_str))

        # Кнопка тестирования будильника
        ttk.Button(
            self.schedule_frame,
            text="Тест будильника",
            command=self.test_alarm
        ).pack(pady=10)

    def show_schedule_editor(self):
        """Окно редактирования расписания"""
        editor = tk.Toplevel(self.root)
        editor.title("Редактирование расписания")
        editor.geometry("500x400")

        # Вкладки для числителя/знаменателя
        notebook = ttk.Notebook(editor)
        notebook.pack(fill=tk.BOTH, expand=True)

        for week_type in ['Числитель', 'Знаменатель']:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=week_type)

            # Заголовок
            ttk.Label(
                frame,
                text=f"Расписание для {week_type} недели",
                style='Header.TLabel'
            ).pack(pady=5)

            # Таблица редактирования
            days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
            for i, day in enumerate(days):
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill=tk.X, padx=5, pady=2)

                ttk.Label(row_frame, text=day, width=15).pack(side=tk.LEFT)

                # Поле для часов
                hours = tk.StringVar()
                current_time = self.wake_up_times[week_type].get(day, time(7, 0))
                hours.set(str(current_time.hour) if isinstance(current_time, time) else "7")

                ttk.Spinbox(
                    row_frame,
                    from_=0,
                    to=23,
                    width=3,
                    textvariable=hours,
                    wrap=True
                ).pack(side=tk.LEFT, padx=2)

                ttk.Label(row_frame, text=":").pack(side=tk.LEFT)

                # Поле для минут
                minutes = tk.StringVar()
                minutes.set(str(current_time.minute) if isinstance(current_time, time) else "0")

                ttk.Spinbox(
                    row_frame,
                    from_=0,
                    to=59,
                    width=3,
                    textvariable=minutes,
                    wrap=True
                ).pack(side=tk.LEFT, padx=2)

                # Сохраняем ссылки на переменные
                self.wake_up_times[week_type][day] = (hours, minutes)

        # Кнопки управления
        btn_frame = ttk.Frame(editor)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame,
            text="Сохранить",
            command=lambda: self.save_schedule(editor)
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            btn_frame,
            text="Отмена",
            command=editor.destroy
        ).pack(side=tk.RIGHT, padx=10)

    def save_schedule(self, editor_window):
        """Сохраняет расписание из редактора"""
        try:
            for week_type in ['Числитель', 'Знаменатель']:
                for day, (hours_var, minutes_var) in self.wake_up_times[week_type].items():
                    hours = int(hours_var.get())
                    minutes = int(minutes_var.get())

                    if not (0 <= hours < 24 and 0 <= minutes < 60):
                        raise ValueError(f"Некорректное время для {day} ({week_type})")

                    self.wake_up_times[week_type][day] = time(hours, minutes)

            self.save_settings()
            self.display_current_schedule()
            editor_window.destroy()
            self.status_var.set("Расписание успешно сохранено")

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def choose_sound(self):
        """Выбор звукового файла для будильника"""
        file_path = filedialog.askopenfilename(
            title="Выберите звуковой файл",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )

        if file_path:
            self.alarm_sound_path = file_path
            self.save_settings()
            self.status_var.set(f"Выбран звук: {os.path.basename(file_path)}")
        else:
            self.status_var.set("Звук не изменен")

    def test_alarm(self):
        """Тестирование будильника"""
        if self.alarm_sound_path:
            try:
                mixer.music.load(self.alarm_sound_path)
                mixer.music.play()
                self.status_var.set("Тестирование звука...")
                # Останавливаем через 3 секунды
                self.root.after(3000, mixer.music.stop)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести звук: {str(e)}")
        else:
            messagebox.showwarning("Внимание", "Сначала выберите звуковой файл")

    def start_alarm_checker(self):
        """Запускает фоновый поток для проверки времени будильника"""
        self.alarm_thread = threading.Thread(target=self.check_alarm, daemon=True)
        self.alarm_thread.start()

    def check_alarm(self):
        """Фоновая проверка времени для срабатывания будильника"""
        while self.running:
            now = datetime.now()
            current_week_type = self.detect_week_type()
            current_day = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"][now.weekday()]

            # Проверяем, нужно ли обновить текущий тип недели в интерфейсе
            if current_week_type != self.current_week_type:
                self.current_week_type = current_week_type
                self.root.after(0, self.update_week_type_display)

            # Проверяем будильник
            wake_time = self.wake_up_times[current_week_type].get(current_day)

            if isinstance(wake_time, time) and now.time() >= wake_time:
                if not mixer.music.get_busy():
                    self.root.after(0, self.trigger_alarm)

            tm.sleep(30)  # Проверяем каждые 30 секунд

    def update_week_type_display(self):
        """Обновляет отображение текущего типа недели"""
        for child in self.header_frame.winfo_children():
            if isinstance(child, ttk.Label):
                child.config(text=f"Текущая неделя: {self.current_week_type}")

        self.display_current_schedule()
        self.status_var.set(f"Автоматически переключено на {self.current_week_type} неделю")

    def trigger_alarm(self):
        """Срабатывание будильника"""
        if self.alarm_sound_path:
            try:
                mixer.music.load(self.alarm_sound_path)
                mixer.music.play(loops=3)  # Проиграть 3 раза

                # Показываем окно с кнопкой отключения
                alarm_window = tk.Toplevel(self.root)
                alarm_window.title("Просыпайся!")
                alarm_window.geometry("300x150")

                ttk.Label(
                    alarm_window,
                    text="Вставай! Пора на занятия!",
                    font=('Arial', 14, 'bold')
                ).pack(pady=20)

                ttk.Button(
                    alarm_window,
                    text="Отключить",
                    command=lambda: self.stop_alarm(alarm_window)
                ).pack(pady=10)

                # Автоматическое отключение через 5 минут
                self.root.after(300000, lambda: self.stop_alarm(alarm_window))

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось воспроизвести будильник: {str(e)}")

    def stop_alarm(self, window):
        """Останавливает будильник"""
        mixer.music.stop()
        if window:
            window.destroy()
        self.status_var.set("Будильник отключен")

    def export_to_csv(self):
        """Экспорт расписания в CSV файл"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("День недели;Числитель;Знаменатель\n")

                    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
                    for day in days:
                        num_time = self.wake_up_times['Числитель'].get(day, time(7, 0))
                        den_time = self.wake_up_times['Знаменатель'].get(day, time(7, 0))

                        num_str = num_time.strftime("%H:%M") if isinstance(num_time, time) else "Не установлено"
                        den_str = den_time.strftime("%H:%M") if isinstance(den_time, time) else "Не установлено"

                        f.write(f"{day};{num_str};{den_str}\n")

                self.status_var.set(f"Расписание экспортировано в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")

    def load_settings(self):
        """Загружает сохраненные настройки"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    for week_type in ['Числитель', 'Знаменатель']:
                        for day, time_str in data['wake_up_times'][week_type].items():
                            if time_str:
                                h, m = map(int, time_str.split(':'))
                                self.wake_up_times[week_type][day] = time(h, m)

                    self.alarm_sound_path = data.get('alarm_sound_path')

            except Exception as e:
                messagebox.showwarning("Ошибка", f"Не удалось загрузить настройки: {str(e)}")

    def save_settings(self):
        """Сохраняет текущие настройки в файл"""
        data = {
            'wake_up_times': {
                'Числитель': {},
                'Знаменатель': {}
            },
            'alarm_sound_path': self.alarm_sound_path
        }

        for week_type in ['Числитель', 'Знаменатель']:
            for day, wake_time in self.wake_up_times[week_type].items():
                if isinstance(wake_time, time):
                    data['wake_up_times'][week_type][day] = wake_time.strftime("%H:%M")
                else:
                    data['wake_up_times'][week_type][day] = ""

        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")

    def on_close(self):
        """Обработчик закрытия окна"""
        self.running = False
        if self.alarm_thread and self.alarm_thread.is_alive():
            self.alarm_thread.join(timeout=1)
        mixer.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WakeUpScheduleApp(root)
    root.mainloop()