from dotenv import load_dotenv
import os

load_dotenv()

BD_LOGIN = os.getenv("BD_LOGIN")
BD_PASSWORD = os.getenv("BD_PASSWORD")
BD_HOST = os.getenv("BD_HOST")
BD_1CAPI = os.getenv("BD_1CAPI")
