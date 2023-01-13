import base64
import re
import tempfile

from pathlib import Path

from flask import Flask, render_template, request, send_file
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired


# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
flask_key = Path('.flask.key')
with flask_key.open('r') as key:
    app.config['SECRET_KEY'] = key.read()


def send_qr_code(raw_encoded_string):
    """Generate the QR code and send it to the client"""

    PADDING_MODULO = 3

    encoded_string = re.sub('[=\r\n]', '', raw_encoded_string.data)

    # Add padding if needed
    if excess_length := (len(encoded_string) % PADDING_MODULO):
        encoded_string += '=' * (PADDING_MODULO - excess_length)

    with tempfile.NamedTemporaryFile(suffix='.jpeg') as image:
        image.write(base64.b64decode(encoded_string))
        image.flush()
        image.seek(0)
        return send_file(image.name, as_attachment=True)


class EntryForm(FlaskForm):
    b64_string = TextAreaField('Encoded string', validators=[DataRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = EntryForm()
    if request.method == 'POST' and form.validate():
        return send_qr_code(form.b64_string)
    return render_template('qr_input.html', form=form)


if __name__ == '__main__':
    app.run()
