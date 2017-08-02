FROM python:3.6

RUN apt-get update \\
	& apt-get install libyaml-dev \\
	& pip install --upgrade pip \\
	& pip install watchdog requests

ADD syncscripts /opt/synccripts
WORKDIR /opt/synccripts
RUN chmod a+x *.py


ADD scripts /opt/scripts
WORKDIR /opt/scripts
RUN chmod a+x *.sh

ENTRYPOINT ["/opt/scripts/entrypoint.sh"]
