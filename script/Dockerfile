FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    apt-utils \
    curl \
    git \
    jq \
    tree \
    nano \
    supervisor\
    && rm -rf /var/lib/apt/lists/*

#RUN  ln -s /etc/supervisor/conf.d /llm/private/scripts/supervisor/

   # ln -s /llm/private/scripts/supervisor/trigger_llm.conf /etc/supervisor/conf.d/link.conf \
  
   #--> per llm call


#RUN pip install --no-cache-dir Jinja2 

CMD ["sleep", "infinity"]
