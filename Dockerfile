FROM python:3.9-alpine

# Deploy version
ARG BUILD_VERSION
ENV BUILD_VERSION=${BUILD_VERSION}

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt && \
  rm /usr/src/app/requirements.txt
COPY . /usr/src/app


CMD [ "/usr/local/bin/python", "/usr/src/app/app.py" ]
