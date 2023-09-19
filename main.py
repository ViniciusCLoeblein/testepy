from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import routes.scripts.main as services

app = FastAPI()

origins = {
    "192.168.102.16",
    "192.168.102.12",
}


@app.middleware("http")
async def check_ip_middleware(request, call_next):
    client_ip = request.client.host
    print(f"IP do cliente: {client_ip}")

    if client_ip not in origins:
        raise HTTPException(status_code=403, detail="IP não permitido")
    response = await call_next(request)
    return response 

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

app.include_router(services.router)
