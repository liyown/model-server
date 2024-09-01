import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError


# 自定义重试装饰器，带有超时控制
def retry_with_timeout(max_attempts, delay, timeout_seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func, *args, **kwargs)
                    try:
                        result = future.result(timeout=timeout_seconds)
                        return result
                    except TimeoutError:
                        print(f"Attempt {attempt + 1} timed out: Operation took longer than {timeout_seconds} seconds")
                    except Exception as e:
                        print(f"Attempt {attempt + 1} failed: {e}")
                    finally:
                        attempt += 1
                        if attempt < max_attempts:
                            time.sleep(delay)
                        else:
                            raise Exception(f"Operation failed after {max_attempts} attempts")

        return wrapper

    return decorator



@retry_with_timeout(max_attempts=3, delay=2, timeout_seconds=5)
def risky_operation():
    print("尝试执行操作...")
    time.sleep(6)  # 模拟长时间运行
    raise Exception("操作失败，重试...")


if __name__ == "__main__":
    try:
        risky_operation()
    except Exception as e:
        print(f"最终失败: {e}")
