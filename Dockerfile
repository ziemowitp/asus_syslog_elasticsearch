FROM fedora:latest

RUN dnf install python3-pip -y && dnf clean all
RUN pip3 install elasticsearch

COPY syslog.py /srv

EXPOSE 514

CMD ["/usr/bin/python3", "/srv/syslog.py"]
