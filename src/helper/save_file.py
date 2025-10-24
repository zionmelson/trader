# src/helper/save_file.py

def save_to_file(data, filename):
    """Saves data to a specified file."""
    with open(filename, "w", encoding="utf-8") as f:
       for line in data:
           f.write(line + "\n")