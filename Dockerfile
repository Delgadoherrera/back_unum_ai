FROM python:3.11.4-slim-buster as builder
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y --no-install-recommends gcc
RUN apt-get install -y libzbar0 libzbar-dev poppler-utils
RUN pip install --upgrade pip
# RUN pip install flake8==6.0.0
COPY . /usr/src/app/
# RUN flake8 --ignore=E501,F401 .
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.11.4-slim-buster
RUN mkdir -p /home/app
RUN addgroup --system app && adduser --system --group app
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME
RUN apt-get update && apt-get install -y --no-install-recommends netcat curl poppler-utils libzbar0
RUN apt-get install -y libgl1-mesa-glx libglib2.0-0
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*
COPY ./entrypoint.sh $APP_HOME
COPY . $APP_HOME
COPY the-byway-410420-9ab864cb800b.json $APP_HOME
RUN chown -R app:app $APP_HOME
USER app
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
