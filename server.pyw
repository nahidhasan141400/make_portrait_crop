from flask import Flask, request, send_file
from rmbg_fn import remove_background_and_center_face
import io
from flask_cors import CORS
import os


# Define your secret key
SECRET_KEY = "nahidhasan141400"


app = Flask(__name__)
# Configure CORS to allow specific origins
CORS(app, resources={r"/api/*": {"origins": ["http://192.168.5.76:5173", "https://edusync.dewanit.com"]}})
CORS(app)

PORT = int(os.environ.get('PORT', 4000))

@app.route('/',  methods=['GET'])
def info():
    return "Welcome to the Face Detection API! By Nahid Hasan 141400", 200

@app.route('/api/remove_bg', methods=['POST'])
def remove_bg():
     # Validate the secret key
    auth_header = request.headers.get('Authorization')
    if auth_header != f"{SECRET_KEY}":
        return "Unauthorized", 401  # Return a 401 Unauthorized response if the key is invalid

    if 'file' not in request.files:
        print("No File Part")
        return "No File Part", 400
    
    file = request.files['file']
    if file.filename == '':
        print("No File Selected")
        return "No File Selected", 400
    
    # Load image and remove background using your preferred method
    input_image = file.read()

    # Call the utility function to process the image
    final_image = remove_background_and_center_face(input_image)
    print(final_image)

    if final_image is None:
        print("no face")
        return "No face detected", 400

    # Prepare the output in a BytesIO object
    output_bytes = io.BytesIO()
    final_image.save(output_bytes, format='PNG')  # Save the image as PNG to the BytesIO stream
    output_bytes.seek(0)  # Move the cursor back to the beginning of the BytesIO object

    return send_file(output_bytes, mimetype='image/png')

if __name__ == '__main__':
    context = ('./certificate.pem', './private_key.pem')
    app.run(host='192.168.5.76',port=PORT,debug=False,ssl_context=context)
    # app.run()
