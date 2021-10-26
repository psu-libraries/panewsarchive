FROM python:3.9.6

WORKDIR /open-oni

RUN adduser app
RUN mkdir -p /open-oni
RUN chown -R app /open-oni

COPY bin/startup /usr/local/bin/startup
RUN chmod +x /usr/local/bin/startup

USER app

ENV PATH=$PATH:/home/app/.local/bin

# Open-Oni Requirements
COPY open-oni/requirements.lock /open-oni
RUN pip install -r requirements.lock --user

# Our requirements on top of Open-Oni
COPY psu-requirements.txt /open-oni
RUN pip install -r psu-requirements.txt --user


COPY --chown=app open-oni /open-oni
COPY --chown=app config/settings_local.py /open-oni/onisite
COPY --chown=app themes /open-oni/themes

CMD ["/usr/local/bin/startup"]
