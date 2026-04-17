import os
import sys

print(f"1. Python: {sys.executable}")
print(f"2. Current folder: {os.getcwd()}")
hadoop_bin = os.path.join(os.getcwd(), "hadoop", "bin", "winutils.exe")
print(f"3. Winutils: {hadoop_bin}")
print(f"4. File exists? {'Y' if os.path.exists(hadoop_bin) else 'N'}")