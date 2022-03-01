import uvicorn
from access360.settings import DEBUG

if __name__ == '__main__':
    uvicorn.run("access360:app", debug=DEBUG, reload=True)