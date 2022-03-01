import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="./env")
DEBUG = os.getenv("DEBUG", None)
SECRET_KEY = os.getenv("SECRET_KEY", None)
REFRESH_KEY = os.getenv("REFRESH_KEY", None)
EMAIL = os.getenv("EMAIL", None)
BUCKET_NAME = os.getenv("bucket", None)
PASSWORD = os.getenv("PASSWORD", None)
ACCESS_TOKEN_EXPIRE_TIME = os.getenv("ACCESS_TOKEN_EXPIRE_TIME", None)
REFRESH_TOKEN_EXPIRE_TIME = os.getenv("REFRESH_TOKEN_EXPIRE_TIME", None)
PAYMENT_SECRET_KEY = os.getenv("RAVE_SECRET_KE", None)
PAYMENT_PUBLIC_KEY = os.getenv("PAYMENT_PUBLIC_KEY", None)
WEBSITE_URL = os.getenv("WEBSITE_URL")
WEBSITE_NAME = "Access360"
API_BASE_URI = "/api/v1"
BASE_DIR =os.path.dirname(os.path.realpath(__file__))
DATABASE_URL = os.getenv("DATABASE_URL")

