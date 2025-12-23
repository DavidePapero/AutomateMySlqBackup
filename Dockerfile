# In production it's probably best to stay on mysql:8
FROM mysql:9.5

LABEL maintainer="Davide Infantino"

RUN mkdir /app
WORKDIR /app

# In production I need this additional library. 
# I left a trace of it in the file: post_processor.py
# RUN curl --output get-pip.py "https://bootstrap.pypa.io/get-pip.py" && \
#     python get-pip.py && \
#     python -m pip install pymysql && \
#    rm get-pip.py

# I want dates in my time zone
# ENV TZ=Europe/Rome

COPY backup.py post_processor.py config.json .

CMD ["python", "-u", "backup.py"]

