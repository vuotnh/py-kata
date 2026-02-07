import asyncio
import uuid


# =========================
# Async Runtime
# =========================
loop = asyncio.new_event_loop() # khởi tạo event loop
queue = None  # Tạo queue task để communication giữa 2 thread
semaphore = None    # limit số task chạy đồng thời


# =========================
# Fake DB ops (REPLACE)
# =========================

TASKS = {}


async def db_update(task_id, **fields):
    TASKS[task_id].update(fields)


def db_create_task(prompt: str) -> str:
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "id": task_id,
        "prompt": prompt,
        "status": "PENDING",
        "result_url": None,
        "error": None,
    }
    return task_id


def db_get_task(task_id: str):
    return TASKS.get(task_id)

# =========================
# Fake async IO (REPLACE)
# =========================

async def gemini_generate_image(prompt: str) -> bytes:
    await asyncio.sleep(2)  # simulate API
    return b"fake_image_bytes"


async def upload_to_s3(data: bytes, key: str) -> str:
    await asyncio.sleep(1)
    return f"https://s3.fake/{key}"


# =========================
# Worker logic
# =========================

async def process_task(task_id: str, prompt: str):
    async with semaphore: # limit số task chạy đồng thời
        try:
            await db_update(task_id, status="RUNNING")

            img = await gemini_generate_image(prompt)

            url = await upload_to_s3(
                img,
                key=f"images/{task_id}.png"
            )

            await db_update(
                task_id,
                status="DONE",
                result_url=url
            )

        except Exception as e:
            await db_update(
                task_id,
                status="FAILED",
                error=str(e)
            )


async def worker_loop():
    while True:
        task_id, prompt = await queue.get() # lấy message từ queue
        asyncio.create_task(process_task(task_id, prompt)) # tạo task và đẩy vào event loop


def start_runtime():
    global queue, semaphore
    asyncio.set_event_loop(loop)        # set main event loop cho thread
    semaphore = asyncio.Semaphore(3)    # Tạo semaphore cho thread
    queue = asyncio.Queue(maxsize=5000) # Khởi tạo queue cho event loop
    loop.create_task(worker_loop())
    loop.run_forever()                  # Khởi chạy event loop
