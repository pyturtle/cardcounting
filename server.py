from flask import Flask, request

app = Flask(__name__)

@app.route('/receive_message', methods=['POST'])
def receive_message():
    data = request.json
    print(f"Received message: {data['message']}")
    return 'Message received', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
