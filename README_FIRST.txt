TOP-NOTCH SHARE — Local Wi-Fi Starter
=====================================

WHAT IT DOES
- Lets a Windows computer act as a local shared-files hub.
- An Android phone and Windows computer on the same Wi-Fi can upload and download files through a browser.
- A six-digit PIN is shown in the Windows terminal.
- Uses Python's standard library; no pip installs are required.

IMPORTANT LIMITS
- This is an early local-network starter, not the finished commercial app.
- It does not yet support QR pairing, trusted-device auto-approval, end-to-end encryption, or internet transfers.
- The PIN is a basic access gate, not production-grade security. Use only on trusted private Wi-Fi.
- Do not expose port 8765 to the public internet.
- Files up to 2 GB are accepted in this starter.

HOW TO RUN ON WINDOWS 10
1. Install Python 3.9 or newer from https://www.python.org/downloads/ and enable "Add Python to PATH".
2. Extract this ZIP to a folder.
3. Double-click start_windows.bat.
4. The terminal shows a PIN and a computer address such as http://192.168.1.25:8765.
5. On the computer, open the local address that includes ?pin=... shown in the terminal.
6. On Android, connect to the same Wi-Fi, open the computer address without the query string, and enter the PIN.
7. Select files on either device to upload them to the computer's shared_files folder. Use Download in the Shared files list to retrieve files.
8. Press Ctrl+C in the terminal to stop sharing.

TROUBLESHOOTING
- If the phone cannot connect, confirm both devices use the same Wi-Fi and that the network does not isolate devices.
- If Windows Firewall asks, allow Python only on Private networks.
- Do not use this starter on public Wi-Fi or networks you do not trust.
