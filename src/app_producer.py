from producer.producer_service import ProducerService
import time

if __name__ == "__main__":
    producer = ProducerService()
    producer.start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
