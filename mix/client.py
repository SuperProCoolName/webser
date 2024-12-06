import socket
from tkinter import *
from tkinter.filedialog import askopenfilename
import os
from threading import Thread


def send(event=None):
    """Отправка сообщений"""
    try:
        msg = my_msg.get()
        my_msg.set("")
        if msg and client:
            if msg.startswith("/file"):  # Проверяем команду для отправки файла
                send_file()
            else:
                client.send(bytes(msg, "utf8"))
        if msg == "/quit":
            client.close()
            top.quit()
    except OSError:
        msg_list.insert(END, "Соединение с сервером разорвано.")


def send_file():
    """Отправка выбранного файла"""
    file_path = askopenfilename()  # Открывает окно выбора файла
    if file_path:
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)

        # Отправка команды на сервер с информацией о файле
        client.send(bytes(f"/file::{filename}::{filesize}", "utf8"))

        # Отправка файла
        with open(file_path, "rb") as f:
            file_data = f.read(1024)
            while file_data:
                client.send(file_data)
                file_data = f.read(1024)

        msg_list.insert(END, f"Вы отправили файл: {filename}")


def receive():
    """Получение сообщений от сервера"""
    while True:
        try:
            # Получаем данные от сервера
            msg = client.recv(1024)

            # Проверяем, если это текстовое сообщение
            if msg.startswith(b"/file"):  # Если это команда для передачи файла
                handle_file(msg)
            else:
                # Пытаемся декодировать как текст
                try:
                    msg = msg.decode("utf-8")
                    msg_list.insert(END, msg)
                except UnicodeDecodeError:
                    print(
                        "Получены данные, которые не могут быть декодированы как UTF-8")
        except Exception as e:
            msg_list.insert(END, f"Ошибка: {str(e)}")
            break


def handle_file(msg):
    """Обработка полученного файла"""
    filename = msg.decode("utf-8").split("::")[1]
    with open(filename, "wb") as f:
        data = client.recv(1024)  # Чтение данных файла
        while data:
            f.write(data)
            data = client.recv(1024)  # Чтение файла частями
    msg_list.insert(END, f"Файл {filename} был получен.")


def on_closing(event=None):
    """Закрытие окна"""
    my_msg.set("/quit")
    send()


# Интерфейс клиента
top = Tk()
top.title("Чат")

messages_frame = Frame(top)
my_msg = StringVar()
scrollbar = Scrollbar(messages_frame)
msg_list = Listbox(messages_frame, height=50, width=150,
                   yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)
msg_list.pack(side=LEFT, fill=BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = Button(top, text="Отправить", command=send)
send_button.pack()
file_button = Button(top, text="Отправить файл",
                     command=send_file)  # Кнопка для отправки файла
file_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

# Настройка клиента
try:
    HOST = "127.0.0.1"
    PORT = 10001
    ADDR = (HOST, PORT)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    receive_thread = Thread(target=receive)  # Используем Thread
    receive_thread.start()
    top.mainloop()
except Exception as e:
    print("Не удалось подключиться к серверу. Ошибка:", e)
    client = None
