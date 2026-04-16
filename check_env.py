import os
import sys

print(f"1. Ваш Python тут: {sys.executable}")
print(f"2. Поточна папка: {os.getcwd()}")
hadoop_bin = os.path.join(os.getcwd(), "hadoop", "bin", "winutils.exe")
print(f"3. Шукаю winutils за шляхом: {hadoop_bin}")
print(f"4. Файл існує? {'ТАК' if os.path.exists(hadoop_bin) else 'НІ'}")