FROM  python:3.7.4
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && echo America/Los_Angeles > /etc/timezone
WORKDIR /
COPY assets/ /
RUN useradd --create-home new_service
RUN apt-get update
RUN apt-get install -y ipython 
RUN rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
