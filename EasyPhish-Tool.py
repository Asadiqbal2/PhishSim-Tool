import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from flask import Flask, render_template_string, request, redirect
import threading
import time

app = Flask(__name__)

email_stats = {
    "total_attempted": 0,
    "total_sent": 0,
    "total_failed": 0,
    "recipients": []
}

# ---------- HTML Templates ----------
dashboard_template = """
<!DOCTYPE html>
<html>
<head>
<title>Email Dashboard</title>
<meta http-equiv="refresh" content="3">
<style>
body { font-family: Arial; background:#f5f5f5; margin:40px; }
.box { background:#fff; padding:30px; max-width:700px; margin:auto; border-radius:8px; }
.ok { color:green; }
.fail { color:red; }
.warn { color:orange; }
</style>
</head>
<body>
<div class="box">
<h2>Email Dashboard</h2>
<p>Attempted: {{ stats.total_attempted }}</p>
<p>Sent: <span class="ok">{{ stats.total_sent }}</span></p>
<p>Failed: <span class="fail">{{ stats.total_failed }}</span></p>
<hr>
{% for r in stats.recipients %}
<p class="{{ r.status }}">{{ r.email }} → {{ r.msg }}</p>
{% endfor %}
<a href="/">Send More Emails</a>
</div>
</body>
</html>
"""

form_template = """
<!DOCTYPE html>
<html>
<head>
<title>Send Emails</title>
<style>
body { font-family: Arial; margin:40px; background:#f5f5f5; }
.box { background:#fff; padding:30px; max-width:700px; margin:auto; border-radius:8px; }
input, textarea, select { width:100%; padding:8px; margin:6px 0; }
button { padding:10px 15px; background:#d4001a; color:#fff; border:none; border-radius:4px; }
</style>
</head>
<body>
<div class="box">
<h2>Email Sending Tool</h2>
<form method="post">

<label>Email Subject</label>
<input type="text" name="subject" placeholder="Enter email subject" required value="Action Required: Update Your Employee Information">

<label>Recipients (comma separated)</label>
<textarea name="recipients" rows="3" required></textarea>

<label>Email Template (HTML allowed)</label>
<textarea name="template" rows="6" required><p>Hello, please update your info.</p></textarea>

<label>SMTP Type</label>
<select name="smtp_type" required>
  <option value="open">Open SMTP Relay</option>
  <option value="gmail">Other SMTP Service</option>
</select>

<div id="auth_fields">
<label>SMTP Username (if using Other SMTP)</label>
<input type="text" name="username" placeholder="example@gmail.com">

<label>SMTP Password</label>
<input type="password" name="password" placeholder="App Password">
</div>

<label>SMTP Server</label>
<input type="text" name="server" placeholder="SMTP Server" required value="smtp.gmail.com">

<label>SMTP Port</label>
<input type="number" name="port" placeholder="SMTP Port" required value="587">

<label>From Email</label>
<input type="email" name="from_email" placeholder="From Email" required>

<button type="submit">Send Emails</button>
</form>
</div>
<script>
// Show/hide auth fields based on SMTP type
const smtpSelect = document.querySelector('select[name="smtp_type"]');
const authFields = document.getElementById('auth_fields');
smtpSelect.addEventListener('change', () => {
    if (smtpSelect.value === 'gmail') authFields.style.display = 'block';
    else authFields.style.display = 'none';
});
authFields.style.display = 'none';
</script>
</body>
</html>
"""

# ---------- Email sending ----------
def send_emails(server, port, from_email, recipients, html_template, smtp_type, username="", password="", subject=""):
    global email_stats
    email_stats["total_attempted"] = len(recipients)
    email_stats["total_sent"] = 0
    email_stats["total_failed"] = 0
    email_stats["recipients"] = []

    for email in recipients:
        result = {"email": email, "status": "fail", "msg": "Failed"}
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = from_email
            msg["To"] = email
            msg["Subject"] = subject
            update_link = "https://employeeportal.com/update-info"
            logo_url = ""
            deadline = datetime.now().replace(day=28).strftime("%B %d, %Y")
            year = datetime.now().year

            plain_text = f"Please update your info before {deadline}."
            html_content = html_template.replace("{deadline}", deadline)

            msg.attach(MIMEText(plain_text, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            if smtp_type == "gmail":
                context = ssl.create_default_context()
                smtp = smtplib.SMTP(server, port)
                smtp.set_debuglevel(1)
                smtp.starttls(context=context)
                smtp.login(username, password)
            else:
                smtp = smtplib.SMTP(server, port, timeout=15)
                smtp.set_debuglevel(1)

            smtp.sendmail(from_email, email, msg.as_string())
            smtp.quit()

            email_stats["total_sent"] += 1
            result["status"] = "ok"
            result["msg"] = "Sent"

        except Exception as e:
            email_stats["total_failed"] += 1
            result["msg"] = f"Failed: {e}"

        email_stats["recipients"].append(result)
        time.sleep(100)

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        recipients = [r.strip() for r in request.form["recipients"].split(",") if r.strip()]
        template = request.form["template"]
        smtp_type = request.form["smtp_type"]
        server = request.form["server"]
        port = int(request.form["port"])
        from_email = request.form["from_email"]
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        subject = request.form["subject"]

        threading.Thread(target=send_emails, args=(server, port, from_email, recipients, template, smtp_type, username, password, subject), daemon=True).start()
        return redirect("/dashboard")

    return render_template_string(form_template)

@app.route("/dashboard")
def dashboard():
    return render_template_string(dashboard_template, stats=email_stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
