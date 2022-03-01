from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect, disconnect
from access360.settings import DEBUG, DATABASE_URL
from fastapi.responses import RedirectResponse
from access360.view import accountView, courseView, cartView, paymentView


app = FastAPI(title="Access360 Api",
              description="Access3060 is an e-learning for people with disabilities",
              debug=DEBUG

              )

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def docs():
    return RedirectResponse("/docs", status_code=302)



@app.on_event("startup")
def Init_database():
    print("database connected successfully")
    connect(host=DATABASE_URL, alias="core")


@app.on_event("shutdown")
def Un_init_database():
    print("database disconnected successfully")
    disconnect()


app.include_router(accountView.router)
app.include_router(courseView.router)
app.include_router(cartView.router)
app.include_router(paymentView.router)

