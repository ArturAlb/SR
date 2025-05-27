from flask import Flask, request, jsonify
import ssl
import os

app = Flask(__name__)
store = {}

@app.route('/signal/<peer>', methods=['GET', 'POST'])
def signal(peer):
    if request.method == 'POST':
        store[peer] = request.json
        return '', 204
    else:
        return jsonify(store.get(peer, {}))

# For gunicorn, just expose 'app'. For local dev, support direct run with SSL.
if __name__ == '__main__':
    cert_path = os.environ.get('SIGNALING_CERT', 'certs/signaling.crt')
    key_path = os.environ.get('SIGNALING_KEY', 'certs/signaling.key')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_path, key_path)
    app.run(host='0.0.0.0', port=8443, ssl_context=context)
