# Digital Healthcare Management System
**Developer: Pari Sangamnerkar**

A robust, full-stack healthcare management portal designed to streamline medical workflows. This system manages patient records, doctor schedules, and billing through a secure, multi-role authentication framework.

## 🚀 Key Features
* **Role-Based Access Control**: Separate dashboards for Admins, Doctors, and Patients.
* **Smart Medical Scanning**: Integrated barcode/QR scanning using `zbar` for prescription management.
* **Automated Billing**: Generates and manages patient invoices efficiently.
* **Dynamic Records**: CRUD operations for patient medical history and doctor availability.

## 🛠️ Technical Stack
* **Backend**: Python (Flask)
* **Database**: SQLAlchemy ORM with SQLite
* **Frontend**: HTML5, CSS3, Bootstrap 5
* **Tools**: Python-zbar, MacOS Terminal

## 🔧 Installation & Setup

To run this project locally on your machine, follow these steps:

### 1. Install System Dependencies
The `zbar` library is required for barcode scanning. 
* **Mac**: `brew install zbar`

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt