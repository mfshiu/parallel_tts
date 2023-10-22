from helper import CircularQueue


# Example usage:
if __name__ == "__main__":
    queue = CircularQueue(10)

    for i in range(1, 15):
        queue.enqueue(i)
        print(f"Enqueued {i}. Queue: {queue}")

    for _ in range(5):
        item = queue.dequeue()
        print(f"Dequeued {item}. Queue: {queue}")
