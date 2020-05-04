import click
import eyed3
import os
import re
import sys

# Изменим уровень логирования в eyed3, чтобы показывать только ошибки.
eyed3.log.setLevel("ERROR")

# Текущая папка, в которой запущен скрипт
current_path = os.getcwd() 

"""Функция print_path возвращает относительный путь папки (относительно директории, в которой запущен скрипт), 
либо абсолютный путь, если папка не является подкаталогом директории, в которой запущен скрипт"""

def print_path(path_dir, file_name):
    rel_path = os.path.join(os.path.relpath(path_dir), file_name) # Относительный путь
    abs_path = os.path.join(path_dir, file_name) # Абсолютный путь
    return rel_path if not ".." in rel_path else abs_path

# Функция delete_special удаляет спецсимволы в тексте тега, пробелы в начале и в конце строки
def delete_special(string):
    if string != None:
        new_string = re.sub(r'[`~!#$@%^&*()=+\\|\/{};:"\',.<>?]+', '', string)
        return new_string.strip()


"""Определяем аргументы командной строки через декоратор click.option
Через соответствующие аргументы click.option задаем предварительные условия значениями по умолчанию.
Добавляем текст справки к нашим аргументам. Он будет показываться при вызове функции через --help"""

@click.command()
#  Аргументы исходной папки, по умолчанию папка, в которой запущен скрипт
@click.option('-s', '--src-dir', default=current_path, help='Source directory.')
#  Аргументы целевой папки, по умолчанию папка, в которой запущен скрипт 
@click.option('-d', '--dst-dir', default=current_path, help='Destination directory.') 
def cli(src_dir, dst_dir):
    try:
        # Содержимое исходной папки - список файлов c расширением mp3
        mp3_list = [elem for elem in os.listdir(src_dir) if elem.endswith(".mp3")]
    # Исключение, если доступ на чтение исходной папки запрещен
    except PermissionError:
        print(
            f'Доступ на чтение папки {src_dir} запрещен'
        )        
        sys.exit()
    # Исключение, если такой исходной папки не существует
    except FileNotFoundError:
        print(
            f'Директория {src_dir} не существует'
        )
        sys.exit()
    # Исключение, если значение не является директорией
    except NotADirectoryError:
        print(
            f'{src_dir} не является директорией'
        )
        sys.exit()

    if not mp3_list:
        print(f'В исходной директории нет файлов mp3')
    else:
        for mp3_name in mp3_list:
            # Абсолютный путь до mp3 файла в исходной папке
            src_path_to_mp3 = os.path.join(src_dir, mp3_name) 
            try:
                # Получаем значения ID3 тегов mp3 файла
                mp3 = eyed3.load(src_path_to_mp3)
                 # Удаление спецсимволов в тексте тега, пробелов в начале и в конце строки
                artist = delete_special(mp3.tag.artist)
                title = delete_special(mp3.tag.album)
                song = delete_special(mp3.tag.title)
                # Если в тегах есть информация об исполнителе и альбоме
                if artist and title: 
                    # Формируем название mp3 файла, либо не меняем, если в тегах нет названия песни
                    mp3_update_name = f"{song} - {artist} - {title}.mp3" if song else mp3_name 
                    # Абсолютный путь до mp3 файла  в целевой папке
                    dst_path_to_mp3 = os.path.join(dst_dir, artist, title,  mp3_update_name) 
                    # Абсолютный путь до каталога mp3 файла в целевой папке
                    dst_mp3_dir = os.path.join(dst_dir, artist, title) 
                    try:
                        # Создаем целевую директорию  и перемещаем в нее mp3 файл 
                        os.renames(src_path_to_mp3, dst_path_to_mp3) 
                        """Логирование, печатаем  абсолютный, либо относительный путь до файла в целевой и
                        исходной папках в зависимости от их расположения относительно текущей директориии скрипта"""
                        print(
                            f"{print_path(src_dir, mp3_name)} -> {print_path(dst_mp3_dir, mp3_update_name)}"
                        )                    
                    except FileExistsError:
                        # Если в целевой директории  файл с таким названием существует, то заменяем его 
                        os.replace(src_path_to_mp3, dst_path_to_mp3)
                        """Логирование, печатаем  абсолютный, либо относительный путь до файла в целевой и
                        исходной папках в зависимости от их расположения относительно текущей директориии скрипта"""
                        print(
                            f"{print_path(src_dir, mp3_name)} -> {print_path(dst_mp3_dir, mp3_update_name)}"
                        )
                    # Исключение, если нет доступа на запись в целевую папку
                    except PermissionError: 
                        print(f'Доступ на запись в целевую папку запрещен')
                        sys.exit()
                # Если в тегах нет информации об исполнителе или альбоме
                else: 
                    print(f'В тегах файла {mp3_name} нет информации об исполнителе или альбоме, файл пропущен')
            # Исключение, если нет доступа на чтение файла
            except PermissionError: 
                print(f'Доступ на чтение файла {mp3_name} запрещен, файл пропущен')
        print(f"Done.")


if __name__ == '__main__':
    cli() # Вызов декорированной функции





