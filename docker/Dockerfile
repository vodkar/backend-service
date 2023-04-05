FROM python:3.10.10-alpine3.17 as base

# Install uvloop dependencies
RUN apk update && apk add postgresql-dev gcc musl-dev linux-headers make

# Set working directory
WORKDIR /opt

# Install dependencies
ADD requirements/base.txt .
RUN pip install --upgrade pip
RUN pip install -r base.txt

# Copy application files
COPY app app

# Expose portx  
EXPOSE 8080

# Run application
CMD ["python", "-m" "app"]

FROM base as test

ADD requirements/test.txt .
RUN pip install -r test.txt
ADD tests tests

ADD pytest.ini .

CMD [ "pytest", "tests/" ]

FROM test as test-debug

RUN pip install debugpy -t /tmp
