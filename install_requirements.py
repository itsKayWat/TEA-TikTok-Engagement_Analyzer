import subprocess
import sys

def install_requirements():
    print("Installing required packages...")
    requirements = [
        'selenium==4.16.0',
        'psutil==5.9.8'
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("\nAll requirements installed successfully!")
    print("\nNote: Make sure you have Chrome browser installed.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    install_requirements() 