#!/usr/bin/env python3
"""LLAMA1 Model Handler"""
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/health')
def health():
    return jsonify({"ok": True, "model": "llama1"})


@app.route('/inference', methods=['POST'])
def inference():
    data = request.json
    # TODO: Load actual model and run inference
    return jsonify({"model": "llama1", "response": "Inference placeholder"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
