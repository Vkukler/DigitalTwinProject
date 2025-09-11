from consumer.consumer_service import ConsumerService
from api.routes import create_api
from config import settings

if __name__ == "__main__":
    consumer_service = ConsumerService()
    consumer_service.start()

    app = create_api(consumer_service)
    app.run(port=settings.FLASK_PORT, debug=True, use_reloader=False)
