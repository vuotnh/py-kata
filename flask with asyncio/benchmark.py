import asyncio
import aiohttp
import time
import statistics
import uuid

async def send_generate_request(session, url, prompt):
    start_time = time.time()
    try:
        async with session.post(url, json={"prompt": prompt}) as response:
            end_time = time.time()
            if response.status == 202:
                data = await response.json()
                task_id = data.get("task_id")
                return {
                    "success": True,
                    "task_id": task_id,
                    "response_time": end_time - start_time,
                    "status_code": response.status
                }
            else:
                return {
                    "success": False,
                    "response_time": end_time - start_time,
                    "status_code": response.status
                }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "response_time": end_time - start_time,
            "error": str(e)
        }

async def benchmark_generate(num_requests, concurrency, base_url):
    url = f"{base_url}/generate"
    prompt = f"Benchmark test {uuid.uuid4()}"
    
    # Tạo semaphore để giới hạn số concurrent requests
    semaphore = asyncio.Semaphore(concurrency)
    
    async def limited_request(session, req_num):
        async with semaphore:
            # Mỗi request có prompt hơi khác nhau
            current_prompt = f"{prompt} - {req_num}"
            return await send_generate_request(session, url, current_prompt)
    
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(num_requests):
            task = asyncio.create_task(limited_request(session, i))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    
    # Phân tích kết quả
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    response_times = [r["response_time"] for r in results]
    
    if successful:
        print(f"Successful requests: {len(successful)}/{num_requests}")
        print(f"Min response time: {min(response_times)*1000:.2f} ms")
        print(f"Max response time: {max(response_times)*1000:.2f} ms")
        print(f"Average response time: {statistics.mean(response_times)*1000:.2f} ms")
        if len(response_times) > 1:
            print(f"Standard deviation: {statistics.stdev(response_times)*1000:.2f} ms")
    else:
        print("No successful requests.")
    
    if failed:
        print(f"Failed requests: {len(failed)}")
        for f in failed[:5]:  # Hiển thị 5 lỗi đầu tiên
            print(f"  - Status: {f.get('status_code')}, Error: {f.get('error')}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python benchmark.py <num_requests> <concurrency> <base_url>")
        print("Example: python benchmark.py 100 10 http://localhost:3000")
        sys.exit(1)
    
    num_requests = int(sys.argv[1])
    concurrency = int(sys.argv[2])
    base_url = sys.argv[3]
    
    asyncio.run(benchmark_generate(num_requests, concurrency, base_url))