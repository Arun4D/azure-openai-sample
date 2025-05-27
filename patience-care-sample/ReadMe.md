# Patience Care Sample

## Run Locally

1. Docker

````bash
docker build -t patient-care-ai .
docker run -p 8000:8000 patient-care-ai
````
2. local machine
````
python -m venv venv
.\venv\Scripts\activate
````

## How to use

✅ Upload a PDF:
````bash
curl -F "file=@sample.pdf" http://localhost:8000/upload_pdf/
````
✅ Query the system:

````bash
curl -X POST -F "query=Summarize the blood test findings" http://localhost:8000/query/
````
✅ Check the root:

````bash
curl http://localhost:8000/
````