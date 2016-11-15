FROM python:2.7-onbuild
ENV FLASK_APP=dcinbox.py
EXPOSE 5000
CMD flask run -h 0.0.0.0 -p 5000
