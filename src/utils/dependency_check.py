import shutil
import sys

def check_tshark():
    """Check whether TShark is available in the system PATH."""
    return shutil.which("tshark")

def show_tshark_status(tshark_path):
    """Display the status of TShark availability."""
    if tshark_path:
        print("TShark is available.")
        print("Path:", tshark_path)
    else:
        print("TShark is not found.")
        print("How to fix:\n1. Install Wireshark.\n2. Make sure TShark is included during installation.\n3. Add TShark to the system PATH if required.\n4. Restart the terminal/application.\n5. Run the dependency checker again.")
        print("You can download it from: https://www.wireshark.org/download.html")
        print("Please install TShark to use this tool.")

def check_pyshark():
    """Checking whether PyShark is installed and available."""
    try:
        import pyshark
        return True
    except ImportError:
        return False
        
def show_pyshark_status(is_available):
    """Display the status of the pyshark"""
    if is_available:
        print("Pyshark is available.")
    else:
        print("Pyshark is not found.")
        print("How to fix:\n1. Install Pyshark using pip: pip install pyshark\n2. Ensure you have the required dependencies installed.\n3. Restart the terminal/application.\n4. Run the dependency checker again.")


def tshark_check():
    """Check whether TShark is available in the system PATH."""
    tshark_path = check_tshark()
    show_tshark_status(tshark_path)

def pyshark_check():
    """Check whether PyShark is installed and available."""
    is_available = check_pyshark()
    show_pyshark_status(is_available)

def python_check():
    """Checking the python version."""
    print("Python version:", sys.version)

def ncap_check():
    """Check whether ncap is available in the system PATH."""
    ncap_path = shutil.which("ncap")
    if ncap_path:
        print("ncap is available.")
        print("Path:", ncap_path)
    else:
        print("ncap is not found.")
        print("How to fix:\n1. Install ncap.\n2. Add ncap to the system PATH if required.\n3. Restart the terminal/application.\n4. Run the dependency checker again.")
        print("Please install ncap to use this tool.")

def all_dependency_check():
    tshark_check()
    pyshark_check()
    python_check()
    ncap_check()
if __name__ == "__main__":
    all_dependency_check()
