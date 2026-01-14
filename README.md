# EasyPhish-Tool

A lightweight Flask-based email sending dashboard that allows controlled bulk email delivery using SMTP.  
This tool provides a simple web interface, real-time delivery statistics, and supports both authenticated and non-authenticated SMTP servers.

> ⚠️ **Important:** This project is intended for **authorized testing, internal notifications, and security research only**.  
> Do **not** use this tool for spam, phishing, or any unauthorized activity.

---

## Features

- Web-based email sending interface
- Supports HTML and plain-text email content
- Real-time dashboard showing:
  - Total emails attempted
  - Successfully sent emails
  - Failed emails with error messages
- SMTP support:
  - Gmail / authenticated SMTP (STARTTLS)
  - Open or unauthenticated SMTP relays
- Configurable sender address, subject, and template
- Background email sending using threads
- Rate-controlled delivery (sleep between emails)

---

## Technology Stack

- Python 3.x
- Flask
- SMTP (`smtplib`)
- HTML (inline templates)
- Threading for background processing

---

## Installation & Running

### 1. Clone the Repository
```bash
git clone https://github.com/Asadiqbal2/EasyPhish-Tool.git
cd EasyPhish-Tool

````

### 2. Install Dependencies
```bash
pip install flask
````
### 3. Run the Application
```bash
python EasyPhish-Tool.py
````
### 4. Access the Web Interface
Open your browser and navigate to:
```bash
http://localhost:5000
````
