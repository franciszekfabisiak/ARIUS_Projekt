import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email details


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

# Sample order details
order_details = {
    "customer_name": "John Doe",
    "pizzas": [
        {
            "name": "Margherita",
            "toppings": ["Tomato", "Mozzarella", "Basil"],
        },
        {
            "name": "Pepperoni",
            "toppings": ["Pepperoni", "Cheese"],
        },
    ],
}

# Load the email template
with open("email_template.html", "r") as template_file:
    template_content = template_file.read()
    print("Template content:", template_content)

# Render the template with order details
template = Template(template_content)
html_content = template.render(order_details)
print(html_content)

# Generated App Password

# Create email
sender_email = "freddyfivebearurur@gmail.com"
recipient_email = "emiliankraska2@wp.pl"
app_password = "eqtm mkmm agud ngsj"

msg = MIMEMultipart("alternative")
msg["Subject"] = "Your Pizza Order Details"
msg["From"] = sender_email
msg["To"] = recipient_email


msg.attach(MIMEText(html_content, "html"))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
