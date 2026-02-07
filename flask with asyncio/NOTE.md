# 1. Inference import
## Bước 1 – import
```python
# trong main.py
from worker import queue
```
`worker.queue` lúc này = `None`

`main.queue` = `None` (bản sao reference ban đầu)

## Bước 2 – start thread

```python
threading.Thread(target=start_runtime).start()
```

Trong  `worker.start_runtime():`
```py
queue = asyncio.Queue(...)
```
❗️ CHỈ update `worker.queue`

❌ `main.queue` KHÔNG thay đổi => biến queue tại main ko được update  

> ***from module import var***  
> 👉 copy reference tại thời điểm import  
> 👉 KHÔNG tự động update khi module thay đổi var sau đó.


## 4. CÁCH FIX ĐÚNG DUY NHẤT
✅ Import CẢ MODULE, KHÔNG import biến    
❌ Sai (đang dùng)  
```python
from worker import start_runtime, loop, queue
```
✅ Đúng  
```python
import worker
while worker.queue is not None:
```

# 2. Khởi tạo queue mồ côi

1. Chỗ sai “khó thấy” nhất

Trong worker.py:
```python
loop = asyncio.new_event_loop()
queue = asyncio.Queue(maxsize=5000)
```

⚠️ Dòng này cực kỳ quan trọng:

`asyncio.Queue()` lấy event loop hiện tại tại thời điểm khởi tạo

Nhưng lúc này:

❌ chưa có `asyncio.set_event_loop(loop)`

❌ chưa có loop nào “active” trong thread

➡️ queue KHÔNG gắn với loop bạn chạy trong `start_runtime`

✅ Nguyên tắc

> Mọi asyncio primitive phải được tạo SAU khi set_event_loop()



❌ Sai
```python
new_event_loop()
create asyncio.Queue()
set_event_loop()
run loop
```

✅ Đúng
```python
new_event_loop()
set_event_loop()
create asyncio.Queue() #  lúc này queue được lấy ra sẽ là queue của event loop hiện tại
run loop
```

Asyncio object ≠ thread-safe
Asyncio object ≠ loop-agnostic

# 3. Put và .result()
Câu lệnh gây block event loop
```python
future = asyncio.run_coroutine_threadsafe(
    worker.queue.put((task_id, prompt)),
    worker.loop
).result(timeout=0.5)
```


Mấu chốt nằm ở đây 👇
```python
.result(timeout=0.5)
```

👉 .result() = blocking call (sync)
Flask thread đứng chờ cho tới khi:

`coroutine queue.put()` chạy xong trong event loop hoặc timeout

**Ngoài ra:**  
`asyncio.Queue.put()` sẽ await nếu:

* queue full
* hoặc loop đang bận
* hoặc backpressure từ consumer

---
# 4. Sử dụng semaphore và asyncio giả lập CCU

