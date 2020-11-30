FROM python:3.7.7-buster
#copy the python imports
COPY requirements.txt .

# install the imports from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#copy all local files to workspace
COPY . .

#expose the container port
EXPOSE 5000

#run the api
CMD ["python3", "predict_api.py"]

