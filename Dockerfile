# Use the official Nginx image as the base image
FROM nginx:latest
# Install cron and python
RUN apt-get update && apt-get install  --no-install-recommends  -y cron python3 python3-pip

# Copy the create_cal.py file to the root directory
RUN  rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED 
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN rm /requirements.txt
COPY create_cal.py /create_cal.py

# Add the cron job to the crontab file
RUN echo "0 1 * * * python3 /create_cal.py" >> /etc/crontab

# Copy the index.html file to the Nginx document root
COPY index.html /usr/share/nginx/html/

EXPOSE 80
# Start the cron service
CMD python3 create_cal.py && cron && nginx -g 'daemon off;'