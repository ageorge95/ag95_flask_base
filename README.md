# AG95 Flask Base

A minimal, yet extensible boilerplate for building Flask applications with a modular structure, background workers, and database integration. This base template provides a solid foundation to kickstart your next Flask project, fostering best practices and rapid development.

---

## Features

* **Modular Design**: Separate modules for server, database, and background workers.
* **Background Workers**: Easy integration with task queues for asynchronous jobs.
* **Configuration Management**: Centralized JSON-based configuration.
* **Requirements Isolated**: `requirements.txt` for dependency management.

---

## Directory Structure

```
ag95_flask_base/
├── db/                  # Database migrations & seed scripts
│   ├── structure.py     # The database structure
├── server/              # Flask application package
│   ├── routes           # HTTP route definitions
│   └── templates        # html templates
├── workers/             # Background worker tasks
├── configuration.json   # Application configuration
├── requirements.txt     # Python dependencies
├── START.py             # Entrypoint to launch server (Python)
├── START.bat            # Windows batch script for START.py
├── Install.bat          # Windows batch script to install dependencies
└── .gitignore           # Files and directories to ignore
```

---

## Getting Started

### Prerequisites

* Python 3.13 is recommended

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/ageorge95/ag95_flask_base.git
   cd ag95_flask_base
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Or on Windows:

   ```bat
   Install.bat
   ```

### Configuration

1. Open `configuration.json` and update fields as needed, for example:

   ```json
   {
    "framework_title": "my_flask_framework",
    "server_port": 5000,
    "db_backup_path": "db_backup"
  }
   ```

### Running the Application

* **Python**

  ```bash
  python START.py
  ```

* **Windows Batch**

  ```bat
  START.bat
  ```

The Flask server will start on the port specified in your configuration (default: 5000).

---

## Usage

* Define new routes in `server/routes`.
* Add database models in `db/structure.py`.
* Implement background tasks in `workers/`.

> **ℹ️INFO:**<br>
> `routes` and `workers` have templates inside to quickly create your routes/ workers

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m "Add YourFeature"`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

---

## Contact

Created and maintained by [@ageorge95](https://github.com/ageorge95). For support or inquiries, please open an issue on GitHub.
