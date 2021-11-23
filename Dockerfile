FROM python:3.9.6 

WORKDIR /open-oni

RUN adduser app && \
  mkdir -p /open-oni && \
  chown -R app /open-oni

RUN apt-get update && apt-get install -y --no-install-recommends \
  krb5-multidev=1.18.3-6+deb11u1 \
  libapr1=1.7.0-6+deb11u1 \
  libgssapi-krb5-2=1.18.3-6+deb11u1 \
  libgssrpc4=1.18.3-6+deb11u1 \
  libk5crypto3=1.18.3-6+deb11u1 \
  libkadm5clnt-mit12=1.18.3-6+deb11u1 \
  libkadm5srv-mit12=1.18.3-6+deb11u1 \
  libkdb5-10=1.18.3-6+deb11u1 \
  libkrb5-3=1.18.3-6+deb11u1 \
  libkrb5-dev=1.18.3-6+deb11u1 \
  libkrb5support0=1.18.3-6+deb11u1 \
  libmariadb-dev-compat=1:10.5.12-0+deb11u1 \
  libmariadb-dev=1:10.5.12-0+deb11u1 \
  libmariadb3=1:10.5.12-0+deb11u1 \
  libpq-dev=13.4-0+deb11u1 \
  libpq5=13.4-0+deb11u1 \
  libssl-dev=1.1.1k-1+deb11u1 \
  libssl1.1=1.1.1k-1+deb11u1 \
  linux-libc-dev=5.10.70-1 \
  mariadb-common=1:10.5.12-0+deb11u1 \
  openssl=1.1.1k-1+deb11u1 && \
  rm -rf /var/lib/apt/lists/* 

COPY bin/startup /usr/local/bin/startup
COPY bin/migrate /usr/local/bin/migrate
RUN chmod +x /usr/local/bin/startup
RUN chmod +x /usr/local/bin/migrate

USER app

ENV PATH=$PATH:/home/app/.local/bin

# Open-Oni Requirements
COPY open-oni/requirements.lock /open-oni
RUN pip install --no-cache-dir -r requirements.lock --user

# Our requirements on top of Open-Oni
COPY psu-requirements.txt /open-oni
RUN pip install --no-cache-dir -r psu-requirements.txt --user

COPY --chown=app open-oni /open-oni
COPY --chown=app config/settings_local.py /open-oni/onisite
COPY --chown=app config/urls.py /open-oni/onisite
COPY --chown=app config/gunicorn.conf.py /open-oni/gunicorn.conf.py
COPY --chown=app themes /open-oni/themes

ADD --chown=app psu-custom/ /open-oni

RUN ["python", "manage.py", "collectstatic", "--noinput"]

CMD ["/usr/local/bin/startup"]
