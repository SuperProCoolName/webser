import os
import hashlib
from multiprocessing import Pool, current_process
import sys
from itertools import product


def get_file_hash(filepath):
    """Вычисляет хеш файла"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def compare_files(file_pair):
    """Сравнивает пару файлов"""
    file1, file2 = file_pair
    pid = os.getpid()

    try:
        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)

        if size1 != size2:
            print(f"PID {pid}: Файлы {file1} и {
                  file2} разные (разные размеры)")
            return False

        hash1 = get_file_hash(file1)
        hash2 = get_file_hash(file2)

        result = hash1 == hash2
        print(f"PID {pid}: Сравнение {file1} и {file2}")
        print(f"Просмотрено байт: {size1}. Результат: {
              'Одинаковые' if result else 'Разные'}")
        return result

    except Exception as e:
        print(f"PID {pid}: Ошибка при сравнении {file1} и {file2}: {str(e)}")
        return False


def main():
    dir1 = input("Введите путь к первому каталогу: ")
    dir2 = input("Введите путь ко второму каталогу: ")
    n_processes = int(input("Введите максимальное количество процессов: "))

    # Получаем списки файлов
    files1 = [os.path.join(dir1, f) for f in os.listdir(
        dir1) if os.path.isfile(os.path.join(dir1, f))]
    files2 = [os.path.join(dir2, f) for f in os.listdir(
        dir2) if os.path.isfile(os.path.join(dir2, f))]

    # Создаем все возможные пары файлов для сравнения
    file_pairs = list(product(files1, files2))

    # Создаем пул процессов
    with Pool(processes=n_processes) as pool:
        # Запускаем сравнение файлов
        pool.map(compare_files, file_pairs)


if __name__ == "__main__":
    main()
