import smtplib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from decouple import config

gmail_user = config('GMAIL_USER')
gmail_password = config('GMAIL_PASSWORD')
p = Path(__file__).parent.parent / 'email_templates'

env = Environment(
    loader=FileSystemLoader(Path(p)),
    autoescape=select_autoescape(['html', 'xml'])
)


def send_template_email(to, subject, template, context={}, debug=False, **kwargs):
    """Sends an email using a template."""
    TEMPLATE = env.get_template(template)
    FROM = 'Scipy Latin America <admin@scipy.lat>'
    TO = to if isinstance(to, list) else [to]
    SUBJECT = subject

    MESSAGE = """From: %s\nTo: %s\nSubject: %s\nContent-Type: text/html\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEMPLATE.render(**context))

    if debug:
        print(TEMPLATE)
    else:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(from_addr=FROM, to_addrs=TO, msg=MESSAGE.encode("iso-8859-1"))
        server.close()


if __name__ == '__main__':
    DEBUG = False
    context = {}
    emails = [
        "email1@email.com",
        "email2@email.com"
    ]
    for email in emails:
        try:
            send_template_email(
                to=email,
                subject='Scipy Latin America Conference - Invitation',
                template='invite.html',
                context=context,
                debug=DEBUG
            )
            print('Email sent!')
        except Exception as e:
            print('Something went wrong...')
            raise e
