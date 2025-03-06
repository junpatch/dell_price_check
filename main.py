from app import create_app
from app.services.scheduler import create_scheduler

app = create_app(config_name="development")
scheduler = create_scheduler(app)

if __name__ == "__main__":
    app.run(debug=True)