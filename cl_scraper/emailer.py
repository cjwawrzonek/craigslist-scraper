import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

""" Quick email function
parameters:
	user:	 a gmail username
	passw: 	 a password to authenticate gmail
	to: 	 recipient address
	subject: email subject
	body: 	 email body plain text
	html:	 formatted html body (optional) """
def send_gmail(user, passw, to, subject, body, html=None):
	sent_from = user + '@gmail.com'

	if html is not None:
		msg = MIMEMultipart('alternative')
		plain = MIMEText(body, 'plain')
		formatted = MIMEText(html, 'html', 'utf-8')

		msg.attach(plain)
		msg.attach(formatted)
	else:
		msg = MIMEText(body)

	msg['Subject'] = subject
	msg['From'] = sent_from
	msg['To'] = to

	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(sent_from, passw)
		server.sendmail(sent_from, to, msg.as_string())
	except:
		pass

	server.close()