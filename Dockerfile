FROM ubuntu:bionic

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
  apache2 \
  ca-certificates \
  gcc \
  git \
  libmysqlclient-dev \
  libssl-dev \
  libxml2-dev \
  libxslt-dev \
  libjpeg-dev \
  mysql-client \
  curl \
  rsync \
  python3-dev \
  python3-venv \
  python3-pip && \
  apt-get -y install --no-install-recommends libapache2-mod-wsgi-py3

# Force apache error logs to stderr
RUN ln -sf /proc/self/fd/1 /var/log/apache2/error.log
# setup apache 
RUN a2enmod cache cache_disk expires rewrite proxy_http ssl
RUN mkdir -p /var/cache/httpd/mod_disk_cache
RUN chown -R www-data:www-data /var/cache/httpd
RUN a2dissite 000-default.conf

# setup shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
# setup base code
WORKDIR /opt/openoni
RUN git clone https://github.com/open-oni/open-oni.git /opt/openoni

# stage entrypoint script
RUN ln -s /opt/openoni/docker/entrypoint.sh /entrypoint.sh
RUN chmod u+x /opt/openoni/docker/entrypoint.sh

RUN echo "/usr/local/bin/manage delete_cache" > /etc/cron.daily/delete_cache
RUN chmod u+x /etc/cron.daily/delete_cache

EXPOSE 80
ENTRYPOINT ./docker/entrypoint.sh
# cmd ["/bin/sleep", "infinity"]
