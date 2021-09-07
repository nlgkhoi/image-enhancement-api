FROM python:3.7-slim as build

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip && pip3 install \
    --user \
    --no-warn-script-location \
#    --no-cache-dir \
    -r requirements.txt

# Copy current folder to docker working dir
COPY . .


FROM python:3.7-slim as output
#Install shared object & library for cv2 (opencv)
RUN apt-get update -y && apt-get install -y --no-install-recommends libgl1-mesa-dev libglib2.0-0 \
 && useradd -m r3v3r \
 && mkdir /app \
 && chown -R r3v3r:r3v3r /app

#RUN apt-get update -y && useradd -m r3v3r \
#  && mkdir /app \
#  && chown -R r3v3r:r3v3r /app


USER r3v3r
WORKDIR /app

ENV PYTHONPATH=/app \
    HOME=/home/r3v3r \
    PATH="/home/r3v3r/.local/bin:${PATH}"

COPY --from=build --chown=r3v3r:r3v3r /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY --from=build --chown=r3v3r:r3v3r /root/.local /home/r3v3r/.local

#COPY --from=build --chown=r3v3r:r3v3r /app/src /app/src
##COPY --from=build --chown=r3v3r:r3v3r /app/models /app/models
#COPY --from=build --chown=r3v3r:r3v3r /app/conf /app/conf
#COPY --from=build --chown=r3v3r:r3v3r /app/main.py /app/main.py

COPY --from=build --chown=r3v3r:r3v3r /app /app

CMD ["python3","/app/main.py", "development"]
