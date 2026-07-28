import shutil



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

if __name__ == "__main__":
    tshark_path = check_tshark()
    show_tshark_status(tshark_path)