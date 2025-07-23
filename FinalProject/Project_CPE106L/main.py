import uvicorn
import multiprocessing
import sys
from app.api.main import app as fastapi_app
from app.ui.main import main as flet_main
from app.models.database import init_db

def run_fastapi():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)

def run_flet():
    flet_main()

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Start FastAPI in a separate process
    api_process = multiprocessing.Process(target=run_fastapi)
    api_process.start()
    
    try:
        # Run Flet UI in the main process
        run_flet()
    finally:
        # Clean up when the app closes
        api_process.terminate()
        api_process.join() 