import asyncio
import paramiko
import openpyxl
from telnetlib3 import open_connection
from aiohttp import web

async def test_telnet(telnet_host, telnet_port, timeout=5):
    try:
        reader, writer = await asyncio.wait_for(open_connection(telnet_host, port=telnet_port), timeout=timeout)
        await asyncio.wait_for(reader.read(1), timeout=timeout)
        writer.close()
        return "Success"
    except (asyncio.TimeoutError, Exception):
        return "Failed"

async def process_excel(file_name, ssh_port, ssh_user, ssh_password):
    wb = openpyxl.load_workbook(file_name)
    ws = wb.active

    for row in ws.iter_rows(min_row=2):  # Skip Header Row
        if all(cell.value is None for cell in row):
            continue

        source_start, source_end, dest_start, dest_end = row[1].value, row[2].value, row[4].value, row[5].value
        try:
            port = int(row[7].value) if row[7].value else 80
        except ValueError:
            row[10].value = "Invalid Port"
            continue

        ssh_user, ssh_password = row[12].value, row[13].value

        all_success = True
        for source_ip in range(int(source_start.split('.')[-1]), int(source_end.split('.')[-1]) + 1):
            source_ip_full = source_start.rsplit('.', 1)[0] + '.' + str(source_ip)
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh_client.connect(source_ip_full, port=ssh_port, username=ssh_user, password=ssh_password)
            except Exception as e:
                row[10].value = "SSH Failed"
                all_success = False
                break

            for dest_ip in range(int(dest_start.split('.')[-1]), int(dest_end.split('.')[-1]) + 1):
                dest_ip_full = dest_start.rsplit('.', 1)[0] + '.' + str(dest_ip)
                result = await test_telnet(dest_ip_full, port)
                if result == "Failed":
                    all_success = False

            ssh_client.close()

        row[10].value = "Success" if all_success else "Failed"

    wb.save(file_name)

async def handle_upload(request):
    reader = await request.multipart()
    field = await reader.next()
    file_name = field.filename
    file_path = '/tmp/check/' + file_name

    with open(file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)

    # Process the uploaded file
    await process_excel(file_path, ssh_port=request.headers.get('ssh-port'),
                       ssh_user=request.headers.get('ssh-user'), ssh_password=request.headers.get('ssh-password'))

    return web.Response(text="File processed successfully")

app = web.Application()
app.router.add_post('/upload', handle_upload)

if __name__ == '__main__':
    web.run_app(app)
