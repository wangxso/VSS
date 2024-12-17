from concurrent.futures import ThreadPoolExecutor, as_completed

# 假设这是我们要运行的任务函数
def task(n):
    import time
    time.sleep(n)  # 模拟耗时操作
    return f"Task {n} completed"

# 提交任务的函数
def submit_task(executor, n):
    future = executor.submit(task, n)
    print(f"Task {n} submitted.")
    return future

# 运行任务并处理结果
def run_tasks():
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [submit_task(executor, i) for i in range(1, 6)]
        
        # 处理完成的任务
        for future in as_completed(futures):
            result = future.result()
            print(result)

if __name__ == "__main__":
    run_tasks()