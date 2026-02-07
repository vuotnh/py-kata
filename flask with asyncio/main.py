import time
import threading
from flask import Flask, request, jsonify
import asyncio

import worker

# Khởi tạo một thread khác để chạy event loop song song với main thread
threading.Thread(
    target=worker.start_runtime,
    daemon=True
).start()

while worker.queue is None:
    time.sleep(0.01)

# =========================
# Flask App
# =========================

app = Flask(__name__)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    prompt = data.get("prompt")

    if not prompt:
        return {"error": "prompt required"}, 400

    task_id = worker.db_create_task(prompt)

    try:
        # Sử dụng run_coroutine_threadsafe để đưa task vào queue một cách async
        future = asyncio.run_coroutine_threadsafe(
            worker.queue.put((task_id, prompt)),
            worker.loop
        ).result(timeout=0.5)
        # Đợi một chút để đảm bảo task được đưa vào queue, nhưng không đợi quá lâu
        future.result(timeout=0.5)

    except Exception:
        return {"error": "server busy"}, 429

    return jsonify({
        "task_id": task_id,
        "status": "PENDING"
    }), 202


@app.route("/status/<task_id>")
def status(task_id):
    task = worker.db_get_task(task_id)
    if not task:
        return {"error": "not found"}, 404
    return jsonify(task)


# =========================
# Entrypoint
# =========================

if __name__ == "__main__":
    app.run(debug=False, port=3000)
