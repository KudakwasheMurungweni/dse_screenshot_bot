import asyncio
from pyppeteer import launch
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def take_screenshot():
    # Launch the browser
    browser = await launch()
    page = await browser.newPage()

    # Open the DSE Webnet page
    await page.goto('https://www.dsewebnet.com')

    # Simulate login (credentials not provided)
    await page.type('#username', os.getenv('DSE_USERNAME'))
    await page.type('#password', os.getenv('DSE_PASSWORD'))
    await page.keyboard.press('Enter')

    # Wait for the page to load
    await page.waitForNavigation()

    # Take a screenshot
    screenshot_filename = f"dse_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    screenshot_path = os.path.join('screenshots', screenshot_filename)
    await page.screenshot({'path': screenshot_path})

    # Close the browser
    await browser.close()

    return screenshot_path

# Run the screenshot function
screenshot_path = asyncio.run(take_screenshot())

# Email the screenshot
email_user = os.getenv('SMTP_USER')
email_password = os.getenv('SMTP_PASSWORD')
email_send = 'w.mapurisa@delta.co.zw'

subject = 'DSE Generator Level Screenshot'

msg = MIMEMultipart()
msg['From'] = email_user
msg['To'] = email_send
msg['Subject'] = subject

body = 'Attached is the daily screenshot of the DSE generator levels.'
msg.attach(MIMEText(body, 'plain'))

with open(screenshot_path, 'rb') as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(screenshot_path)}")
    msg.attach(part)

text = msg.as_string()

# Using Outlook SMTP server
server = smtplib.SMTP('smtp.office365.com', 587)
server.starttls()
server.login(email_user, email_password)
server.sendmail(email_user, email_send, text)
server.quit()
