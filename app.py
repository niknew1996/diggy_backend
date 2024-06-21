from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openpyxl
import asyncio
import paramiko
from telnetlib3 import open_connection
import os

app = Flask(__name__)
CORS(app)

# Function to handle Telnet
async def test_telnet(telnet_host, telnet_port, timeout=5):
    try:
        reader, writer = await asyncio.wait_for(open_connection(telnet_host, port=telnet_port), timeout=timeout)
        await asyncio.wait_for(reader.read(1), timeout=timeout)
        writer.close()
        return "Success"
    except (asyncio.TimeoutError, Exception):
        return "Failed"

@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    ssh_user = request.form['ssh_user']
    ssh_password = request.form['ssh_password']

    # Save the file to a temporary location
    temp_dir = "/tmp"
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)

    wb = openpyxl.load_workbook(file_path)
    ws = wb.active

    for row in ws.iter_rows(min_row=2):
        if all(cell.value is None for cell in row):
            print("Row is Null stop it")
            break

        source_start, source_end, dest_start, dest_end = row[1].value, row[2].value, row[4].value, row[5].value
        try:
            port = int(row[7].value) if row[7].value else 80
        except ValueError:
            row[10].value = "Invalid Port"
            continue

        ssh_port = 22

        all_success = True
        for source_ip in range(int(source_start.split('.')[-1]), int(source_end.split('.')[-1]) + 1):
            source_ip_full = source_start.rsplit('.', 1)[0] + '.' + str(source_ip)

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh_client.connect(source_ip_full, port=ssh_port, username=ssh_user, password=ssh_password)
                print(f"SSH connection to {source_ip_full} successful")
            except Exception as e:
                print(f"An error occurred when connecting to {source_ip_full}: {e}")
                row[10].value = "SSH Failed"
                all_success = False
                break

            for dest_ip in range(int(dest_start.split('.')[-1]), int(dest_end.split('.')[-1]) + 1):
                dest_ip_full = dest_start.rsplit('.', 1)[0] + '.' + str(dest_ip)
                print(f"Testing telnet from {source_ip_full} to {dest_ip_full}:{port}")
                result = asyncio.run(test_telnet(dest_ip_full, port))
                print(f"Testing telnet result: {result}")
                if result == "Failed":
                    all_success = False

            ssh_client.close()

        row[10].value = "Success" if all_success else "Failed"

    result_filename = os.path.join(temp_dir, "result.xlsx")
    wb.save(result_filename)

    return send_file(result_filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
