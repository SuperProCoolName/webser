import socket
from threading import Thread  # Импортируем Thread

clients = {}
addresses = {}

# Функция отправки сообщений всем клиентам


def broadcast(msg, name=""):
    # Список копируем, чтобы избежать ошибок при удалении клиента
    for sock in list(clients.keys()):
        try:
            sock.send(bytes(name, "utf8") + msg)
        except Exception:
            sock.close()
            del clients[sock]

# Функция обработки одного клиента


def handle_client(client):
    try:
        # Получаем имя клиента
        name = client.recv(1024).decode("utf8")
        welcome = f"Теперь вы в чате, {name}!"
        client.send(bytes(welcome, "utf8"))
        broadcast(
            bytes(f"Пользователь {name} зашёл в чат, поприветствуйте его!", "utf8"))
        clients[client] = name

        while True:
            msg = client.recv(1024)

            if not msg:  # Если нет сообщения, клиент отключился
                break

            if msg.startswith(b"/file"):  # Проверка, что пришла команда /file
                handle_file(client, msg)
            else:
                try:
                    # Если это текстовое сообщение, то декодируем как UTF-8
                    text_msg = msg.decode("utf-8")
                    broadcast(msg, name + ": ")
                except UnicodeDecodeError:
                    # Пропускаем некорректные данные (например, файлы)
                    print(
                        "Получены данные, которые не могут быть декодированы как UTF-8")
                    continue  # Пропускаем некорректные данные

    finally:
        client.close()
        if client in clients:
            name = clients[client]
            del clients[client]
            broadcast(bytes(f"{name} покинул чат.", "utf8"))

# Функция обработки файла


def handle_file(client, msg):
    """Обработка отправки файлов от клиента"""
    try:
        # Разделим сообщение на части: команда /file, имя файла и размер файла
        header = msg.decode("utf8").split("::")

        # Проверяем, что в сообщении три части
        if len(header) != 3:
            print("Ошибка: неверный формат команды /file.")
            return

        filename = header[1]
        filesize = int(header[2])

        print(f"Получаем файл: {filename}, размер: {filesize} байт")

        # Получаем сам файл
        with open(filename, "wb") as f:
            total_received = 0
            while total_received < filesize:
                data = client.recv(1024)  # Получаем данные по частям
                if not data:
                    break
                f.write(data)
                total_received += len(data)

        # Отправляем всем участникам чат уведомление о получении файла
        broadcast(bytes(f"Файл {filename} был отправлен в чат.", "utf8"))
    except Exception as e:
        print(f"Ошибка при получении файла: {e}")

# Эта функция постоянно слушает входящие соединения с помощью метода server.accept()
# handle_client(client): Эта функция обрабатывает одно подключение. Она выполняет следующие задачи: Получает имя клиента.
# Отправляет приветственное сообщение.
# Следит за входящими сообщениями от клиента.
# Если клиент отправляет текстовое сообщение, оно ретранслируется всем другим клиентам.
# Если клиент отправляет команду на отправку файла (/file), сервер начинает принимать файл и сохраняет его.
# Если клиент отключается, его соединение закрывается.


def accept_incoming_connections():
    while True:
        client, client_address = server.accept()
        print(f"{client_address} подключился.")
        client.send(bytes("Введите ваше имя в поле ниже", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)
               ).start()  # Используем Thread


# Настройка сервера
HOST = ''
PORT = 10001
BUFSIZ = 1024
ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(5)
print("Сервер запущен.")
ACCEPT_THREAD = Thread(target=accept_incoming_connections)  # Используем Thread
ACCEPT_THREAD.start()
ACCEPT_THREAD.join()
server.close()
