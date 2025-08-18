from fastapi import FastAPI
from lynx_logger import LynxLogger, Level, Format
from lynx_logger.config import LogConfig, FileConfig
from lynx_logger.middleware import FastAPILoggingMiddleware


logger = LynxLogger(
    LogConfig(
        name="fastapi_app", 
        level=Level.INFO, 
        format=Format.JSON, 
        log_to_console=True, 
        file=FileConfig(
            enabled=True,
            filename="fastapi_app.log",
            max_size="10MB",
            backup_count=5,
            delay=True
        )
    )
)

app = FastAPI()


middleware = FastAPILoggingMiddleware(logger=logger.get_logger())
app.middleware("http")(middleware(app))

@app.get("/")
def read_root():
    logger.info("Hello, World!")
    return {"Hello": "World"}

if __name__ == "__main__": # or uvicorn fastapi_app:app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)