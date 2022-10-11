FROM python:3.9.6 

WORKDIR /open-oni

RUN adduser app && \
  mkdir -p /open-oni && \
  chown -R app /open-oni

RUN apt-get update && apt-get install -y --no-install-recommends \
  krb5-multidev \
  libapr1 \
  libgssapi-krb5-2 \
  libgssrpc4 \
  libk5crypto3 \
  libkadm5clnt-mit12 \
  libkadm5srv-mit12 \
  libkdb5-10 \
  libkrb5-3 \
  libkrb5-dev \
  libkrb5support0 \
  libmariadb-dev-compat \
  libmariadb-dev \
  libmariadb3 \
  libpq-dev \
  libpq5 \
  libssl-dev \
  libssl1.1 \
  linux-libc-dev \
  mariadb-common \
  openssl && \
  rm -rf /var/lib/apt/lists/* 

COPY bin/startup /usr/local/bin/startup
COPY bin/migrate /usr/local/bin/migrate
RUN chmod +x /usr/local/bin/startup
RUN chmod +x /usr/local/bin/migrate

USER app

ENV PATH=$PATH:/home/app/.local/bin

# Open-Oni Requirements
COPY open-oni/requirements.lock /open-oni
# RUN pip install --no-cache-dir -r requirements.lock --user

# Our requirements on top of Open-Oni
COPY psu-requirements.txt /open-oni
RUN pip install --no-cache-dir -r psu-requirements.txt --user

COPY --chown=app open-oni /open-oni
COPY --chown=app config/settings_local.py /open-oni/onisite
COPY --chown=app config/urls.py /open-oni/onisite
COPY --chown=app themes /open-oni/themes

ADD --chown=app psu-custom/ /open-oni

RUN ["python", "manage.py", "collectstatic", "--noinput"]

CMD ["/usr/local/bin/startup"]
