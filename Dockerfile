FROM ubuntu:trusty
ENV DEBIAN_FRONTEND noninteractive
ENV CORS_ORIGIN *

# setup tools
RUN apt-get update --yes --force-yes
RUN apt-get install --yes --force-yes build-essential python python-dev python-setuptools python-pip curl
RUN apt-get install --yes --force-yes python-software-properties

RUN apt-get install --yes --force-yes nginx supervisor
RUN pip install uwsgi

# Add and install Python modules
ADD . /resolver-api
RUN pip install -r /resolver-api/requirements.txt

# configuration
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /resolver-api/conf/nginx-app.conf /etc/nginx/sites-enabled/
RUN ln -s /resolver-api/conf/supervisor-app.conf /etc/supervisor/conf.d/

# Expose - note that load balancer terminates SSL
EXPOSE 80

# RUN
CMD ["supervisord", "-n"]
