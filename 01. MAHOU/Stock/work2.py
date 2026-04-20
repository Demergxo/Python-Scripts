import os


base_path = os.getcwd()

RAW_DIR = base_path+r"\raw_files"
user = os.getenv("USERNAME")
print(RAW_DIR)
print(user)