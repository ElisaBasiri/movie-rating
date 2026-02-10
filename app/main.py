from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.controllers.movie_controller import router as movie_router
from app.exceptions.custom_exceptions import NotFoundException, ValidationException

app = FastAPI()
app.include_router(movie_router)

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "failure", "error": {"code": exc.status_code, "message": exc.detail}},
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "failure", "error": {"code": exc.status_code, "message": exc.detail}},
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "failure", "error": {"code": 422, "message": str(exc)}},
    )