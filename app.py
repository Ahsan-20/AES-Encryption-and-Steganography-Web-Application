from flask import Flask, render_template, request, send_file
from finalized import aes_encrypt, aes_decrypt, encode_image, decode_image
from PIL import Image
from tempfile import NamedTemporaryFile
import random
import string
app = Flask(__name__)

def generate_random_filename(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length)) + '.png'

@app.route('/')
def index():
    return render_template('encryption.html')  

@app.route('/decrypt')
def decrypt_page():
    return render_template('decryption.html')  

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'image' not in request.files:
        return 'No image file', 400
    image = request.files['image']
    message = request.form['message']
    key = request.form['key']

    if not message or not key:
        return 'Missing message or key', 400

    try:
        encrypted_message = aes_encrypt(message, key)
        img = Image.open(image)
        encoded_image = encode_image(img, encrypted_message)
        filename = generate_random_filename()
        with NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            encoded_image.save(temp_file, format='PNG')
            temp_file_path = temp_file.name  
        return send_file(
            temp_file_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename  
        )
    except Exception as e:
        return f'An error occurred: {str(e)}', 500

@app.route('/decrypt_message', methods=['POST'])
def decrypt_message():
    if 'image' not in request.files:
        return 'No image file', 400
    image = request.files['image']
    key = request.form['key']

    try:
        img = Image.open(image)
        extracted_encrypted_message = decode_image(img)
        decrypted_message = aes_decrypt(extracted_encrypted_message, key)
        return decrypted_message
    except Exception as e:
        return f'An error occurred: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=False)