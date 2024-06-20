# Flask Backend for Server Communication Checker

This project provides a Flask-based backend that checks the communication between source and destination servers via Telnet, using data provided in an Excel file. The backend supports SSH connections to the source servers and verifies connectivity to the destination servers.

## Features

- Upload an Excel file (.xlsx) with server details.
- SSH into source servers using provided credentials.
- Check Telnet connectivity to destination servers.
- Save results in the Excel file and allow for download.

## Prerequisites

- Python 3.x
- Docker (optional, for containerized deployment)

## Setup

### Local Setup

1. **Clone the repository**:
    ```bash
    git clone https://your-repo-url
    cd your-repo-directory
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Flask application**:
    ```bash
    export FLASK_APP=app.py
    flask run
    ```

    The application will be available at `http://127.0.0.1:5000`.

### Docker Setup

1. **Build the Docker image**:
    ```bash
    docker build -t backend_image .
    ```

2. **Run the Docker container**:
    ```bash
    docker run -d -p 5000:5000 --name backend_container backend_image
    ```

    The application will be available at `http://127.0.0.1:5000`.

## API Endpoints

- `POST /upload`: Upload the Excel file.
- `GET /download`: Download the processed Excel file.

## Environment Variables

- `FLASK_ENV`: Set to `development` for development mode.

## Project Structure
```
project_diggy/
│
├── backend/               # Backend (Python/Flask)
│   ├── app.py             # Main application file
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Docker configuration for backend
│
└── frontend/               # Frontend (React)
    ├── package.json        # Node.js dependencies
    ├── package-lock.json   # Lockfile for Node.js dependencies
    ├── public/             # Static files (e.g., index.html)
    └── src/                # Source code of the React application
    ├── Dockerfile          # Docker configuration for frontend
    ├── dist/               # Build output directory
    └── node_modules/       # Node.js modules (installed by npm)
```
#### Usage
1. Upload Excel file via the /upload endpoint.
2. The backend processes the file and checks connectivity.
3. Download the results via the /download endpoint.
#### Troubleshooting
- Ensure that all dependencies are installed correctly.
- Verify that Docker is installed and running if using Docker.
- Check for sufficient disk space if you encounter issues during Docker image load.
## License
```css
This project is licensed under the MIT License. See the LICENSE file for details.
```