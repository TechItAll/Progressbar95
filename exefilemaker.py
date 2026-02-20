import subprocess
import sys
import os

def python_to_exe(python_file, output_name=None):
    """Convert a Python file to an executable using PyInstaller"""
    
    if not os.path.exists(python_file):
        print(f"Error: File '{python_file}' not found")
        return False
    
    if output_name is None:
        output_name = os.path.splitext(python_file)[0]
    
    try:
        print(f"Converting {python_file} to exe...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "pyinstaller"
        ], check=True)
        
        subprocess.run([
            "pyinstaller", "--onefile", "--windowed",
            f"--name={output_name}",
            python_file
        ], check=True)
        
        print(f"Success! Executable created in ./dist/{output_name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    python_file = input("Enter the Python file path: ")
    output_name = input("Enter output exe name (or press Enter for default): ").strip()
    
    python_to_exe(python_file, output_name if output_name else None)