FROM python:3.7.7-buster
#copy the python imports
COPY requirements.txt .

# install the imports from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#copy all local files to workspace
COPY . .

#expose the container port
EXPOSE 5001

ENV HASHTAGS ["#Covid", "#COVID", "#Covid19", "#covid", "#COVID", "#covid19"]
ENV location_api http://predict:5000/predict
ENV vis_api http://vis:8050/update_avg
#run the api
CMD ["python3", "client.py"]

