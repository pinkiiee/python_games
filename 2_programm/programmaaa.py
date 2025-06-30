# Импорт библиотек
import json
import os # проверка существования файла перед загрузкой
from datetime import time, datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import pygame

class WakeUpScheduleApp:
    def __init__(self, root):     #Конструктор класса, для создания объектов
        self.root = root
        self.root.title("Расписание Побудок")

        # загрузка сохранённых данных (если есть)
        self.wake_up_times = self.load_from_json() or {'Числитель': {}, 'Знаменатель': {}} # либо загружает из json, либо создает новый словарь
        self.alarm_time = None
        self.alarm_sound_path = None
        self.schedule_displayed = False

        self.create_widgets()

    def create_widgets(self): # создание начальных виджетов программы (функция, метод)
        self.label_welcome = tk.Label(
            self.root,
            text="Здравствуй, уважаемый студент! Ты хотел бы проснуться завтра вовремя?"
        )
        self.label_welcome.pack(pady=10) # отступы

        self.button_yes = tk.Button(
            self.root,
            text="Да",
            command=self.show_input,
            bg = "green") # bg - background - фон
        self.button_no = tk.Button(self.root, text="Нет", command=self.exit_app)

        self.button_yes.pack(side=tk.LEFT, padx=20)
        self.button_no.pack(side=tk.RIGHT, padx=20)

    def show_input(self): # создание интерфейса для ввода/редактирования расписания
        # очистка предыдущих виджетов для создания новых
        for widget in self.root.winfo_children():
            widget.destroy()

        self.label_instructions = tk.Label(
            self.root,
            text="Хорошо, тогда выбери пожалуйста время своего пробуждения на каждый учебный день!"
        )
        self.label_instructions.pack(pady=10)

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        # списки дней недели
        days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        weeks = ["Числитель", "Знаменатель"]

        for week in weeks:
            label_week = tk.Label(self.frame, text=week, font=("Arial", 12, "bold"))
            label_week.grid(row=0, column=weeks.index(week) * 4 + 1, columnspan=3, padx=10, pady=5)

        for day_idx, day in enumerate(days_of_week):
            label_day = tk.Label(self.frame, text=day)
            label_day.grid(row=day_idx + 1, column=0, padx=10, pady=5)

            # спинбоксы
            for week in weeks:
                hour_label = tk.Label(self.frame, text="Часы:")
                hour_spinbox = tk.Spinbox(self.frame, from_=0, to=23, width=5, format="%02.0f")
                minute_label = tk.Label(self.frame, text="Минуты:")
                minute_spinbox = tk.Spinbox(self.frame, from_=0, to=59, width=5, format="%02.0f")

                # заполняем существующими значениями, если они есть
                if day in self.wake_up_times[week]:
                    wake_time = self.wake_up_times[week][day]
                    if isinstance(wake_time, time):
                        hour_spinbox.delete(0, tk.END)
                        hour_spinbox.insert(0, wake_time.hour)
                        minute_spinbox.delete(0, tk.END)
                        minute_spinbox.insert(0, wake_time.minute)

                col_offset = weeks.index(week) * 4
                hour_label.grid(row=day_idx + 1, column=col_offset + 1, padx=5, pady=5)
                hour_spinbox.grid(row=day_idx + 1, column=col_offset + 2, padx=5, pady=5)
                minute_label.grid(row=day_idx + 1, column=col_offset + 3, padx=5, pady=5)
                minute_spinbox.grid(row=day_idx + 1, column=col_offset + 4, padx=5, pady=5)

                # сохраняем ссылки на спинбоксы
                if week not in self.wake_up_times:
                    self.wake_up_times[week] = {}
                self.wake_up_times[week][day] = (hour_spinbox, minute_spinbox)

        # кнопки управления
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        self.button_submit = tk.Button(button_frame, text="Сохранить", command=self.save_schedule)
        self.button_submit.pack(side=tk.LEFT, padx=10)

        self.button_show = tk.Button(button_frame, text="Показать расписание", command=self.display_schedule)
        self.button_show.pack(side=tk.LEFT, padx=10)

        self.button_set_alarm = tk.Button(self.root, text="Установить будильник", command=self.set_alarm)
        self.button_set_alarm.pack(pady=10)

    def exit_app(self):
        # закрывает программу
        messagebox.showinfo("Пожалеешь, пожалеешь...", "А зря... Мы могли бы тебе помочь :(")
        self.root.destroy()

    def save_to_json(self):
        # сохраняет wake_up_times в json файл
        try:
            # преобразуем time в строку (т.к. time в json не поддерживается)
            serializable_data = {
                week: {
                    day: (t.strftime("%H:%M") if isinstance(t, time) else None)
                    for day, t in days.items()
                }
                for week, days in self.wake_up_times.items()
            }
            with open("wake_up_schedule.json", "w", encoding="utf-8") as f:
                json.dump(serializable_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_from_json(self):
        # загружает wake_up_times из файла json (если он есть)
        if not os.path.exists("wake_up_schedule.json"):
            return None

        try:
            with open("wake_up_schedule.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                # преобразуем строки обратно в time
                loaded_data = {
                    week: {
                        day: (
                            datetime.strptime(time_str, "%H:%M").time()
                            if time_str else None
                        )
                        for day, time_str in days.items()
                    }
                    for week, days in data.items()
                }
                return loaded_data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            return None

    def save_schedule(self):
    # сохранение расписания
        try:
            new_wake_up_times = {'Числитель': {}, 'Знаменатель': {}}

            for week, days in self.wake_up_times.items():
                for day, (hour_spinbox, minute_spinbox) in days.items():
                    hours = int(hour_spinbox.get())
                    minutes = int(minute_spinbox.get())
                    if not (0 <= hours < 24 and 0 <= minutes < 60):
                        raise ValueError(f"Некорректное время для {day} ({week})") # raise -    механизм защиты от неверных данных
                    new_wake_up_times[week][day] = time(hours, minutes)

            # обновляем данные и сохраняем в json
            self.wake_up_times = new_wake_up_times
            self.save_to_json()
            messagebox.showinfo("Сохранено", "Расписание успешно сохранено!")

            # если расписание уже отображается, обновляем его
            if self.schedule_displayed:
                self.display_schedule()

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def display_schedule(self):
        # отображает сохраненное расписание
        # очистка предыдущих виджетов
        for widget in self.root.winfo_children():
            widget.destroy()

        self.schedule_displayed = True

        self.label_schedule = tk.Label(self.root, text="Ваше расписание пробуждений:")
        self.label_schedule.pack(pady=10)

        frame_schedule = tk.Frame(self.root)
        frame_schedule.pack()

        days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        weeks = ["Числитель", "Знаменатель"]

        for week in weeks:
            label_week = tk.Label(frame_schedule, text=week, font=("Arial", 12, "bold"))
            label_week.grid(row=0, column=weeks.index(week) + 1, padx=10, pady=5)

        for day_idx, day in enumerate(days_of_week):
            label_day = tk.Label(frame_schedule, text=day)
            label_day.grid(row=day_idx + 1, column=0, padx=10, pady=5)

            for week in weeks:
                wake_time = self.wake_up_times[week].get(day)
                if isinstance(wake_time, time):
                    label_time = tk.Label(frame_schedule, text=wake_time.strftime("%H:%M"))
                else:
                    label_time = tk.Label(frame_schedule, text="Не указано")
                label_time.grid(row=day_idx + 1, column=weeks.index(week) + 1, padx=10, pady=5)

        # кнопки управления
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        self.button_edit = tk.Button(button_frame, text="Редактировать", command=self.show_input)
        self.button_edit.pack(side=tk.LEFT, padx=10)

        self.button_set_alarm = tk.Button(self.root, text="Установить будильник", command=self.set_alarm)
        self.button_set_alarm.pack(pady=10)

    def set_alarm(self):
    # установка будильника
        if not self.alarm_sound_path: # если звук не выбран, то метод choose_sound
            self.choose_sound()

        alarm_window = tk.Toplevel(self.root)
        alarm_window.title("Установить будильник")

        label_hour = tk.Label(alarm_window, text="Часы (0-23):")
        label_hour.grid(row=0, column=0, padx=5, pady=5)
        hour_spinbox = tk.Spinbox(alarm_window, from_=0, to=23, width=5)
        hour_spinbox.grid(row=0, column=1, padx=5, pady=5)

        label_minute = tk.Label(alarm_window, text="Минуты (0-59):")
        label_minute.grid(row=1, column=0, padx=5, pady=5)
        minute_spinbox = tk.Spinbox(alarm_window, from_=0, to=59, width=5)
        minute_spinbox.grid(row=1, column=1, padx=5, pady=5)

        def start_alarm():
            try:
                hours = int(hour_spinbox.get())
                minutes = int(minute_spinbox.get())
                if not (0 <= hours < 24 and 0 <= minutes < 60):
                    raise ValueError("Некорректное время будильника")
                alarm_time = time(hours, minutes)
                self.alarm_time = alarm_time
                threading.Thread(target=self.check_alarm).start()
                messagebox.showinfo("Будильник", f"Будильник установлен на {alarm_time.strftime('%H:%M')}")
                alarm_window.destroy()
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))

        button_set = tk.Button(alarm_window, text="Установить", command=start_alarm)
        button_set.grid(row=2, column=0, columnspan=2, pady=10)

    def choose_sound(self):
        # функция для выбора звукового файла
        file_path = filedialog.askopenfilename(
            title="Выберите звуковой файл",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )
        if file_path:
            self.alarm_sound_path = file_path
            messagebox.showinfo("Звук выбран", f"Выбранный звук: {file_path}")
        else:
            messagebox.showwarning("Звук не выбран", "Пожалуйста, выберите звуковой файл.")

    def check_alarm(self):
        pygame.mixer.init()
        # проверка, наступило ли время для будильника
        while True:
            if self.alarm_time:
                current_time = datetime.now().time()
                if current_time >= self.alarm_time:
                    if self.alarm_sound_path:
                        pygame.mixer.music.load(self.alarm_sound_path)
                        pygame.mixer.music.play(-1)

                    messagebox.showinfo("Будильник", "Просыпайся!")
                    pygame.mixer.music.stop()
                    break


if __name__ == "__main__":
    root = tk.Tk() # главное окно
    app = WakeUpScheduleApp(root) # экземпляр программы
    root.mainloop() # цикл обработки событий