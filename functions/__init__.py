from queue import Queue

my_queue = Queue()


def return_thread_value(f):
    def wrapper(*args):
        my_queue.put(f(*args))

    return wrapper
