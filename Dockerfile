FROM fedora:22

ENV FEDORA_VERSION 22

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

WORKDIR /

RUN yum -y install dnf \
    && dnf clean all \
    && dnf -y install http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-"$FEDORA_VERSION".noarch.rpm \
    && dnf -y update \
    && dnf -y distro-sync \
    && dnf -y groupinstall "Minimal Install" "Development Tools" "Development Libraries" \
    && dnf -y install patch tar wget libcurl curl libcurl-devel htop mc nano vim psmisc iotop \
    && dnf -y install ffmpeg ffmpeg-devel gifsicle ImageMagick ImageMagick-devel \
    && dnf -y install turbojpeg turbojpeg-devel openjpeg openjpeg-devel libxslt libxslt-devel libxml2 libxml2-devel libffi libffi-devel libev libev-devel libevent libevent-devel libuv libuv-devel libmemcached libmemcached-devel postgresql postgresql-devel \
    && dnf -y install java-1.8.0-openjdk java-1.8.0-openjdk-devel \
    && dnf -y install npm nodejs nodejs-devel \
    && dnf -y install ruby ruby-devel rubygem-bundler rubygem-rake \
    && dnf clean all

# && dnf -y install http://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-"$FEDORA_VERSION".noarch.rpm \

RUN mkdir /src /yaga

WORKDIR /src

ENV PYTHON_VERSION 2.7.9
ENV PYTHON_URL https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
ENV SETUPTOOLS_VERSION 17.0
ENV SETUPTOOLS_URL https://pypi.python.org/packages/source/s/setuptools/setuptools-17.0.tar.gz

RUN wget "$PYTHON_URL" \
    && tar xvf Python-"$PYTHON_VERSION".tgz \
    && cd Python-"$PYTHON_VERSION" \
    && ./configure --prefix=/opt/python-ucs4 --with-ensurepip=no --enable-unicode=ucs4 \
    && make \
    && make install \
    && cd .. \
    && wget "$SETUPTOOLS_URL" \
    && tar xvf setuptools-"$SETUPTOOLS_VERSION".tar.gz \
    && cd setuptools-"$SETUPTOOLS_VERSION" \
    && /opt/python-ucs4/bin/python setup.py install \
    && /opt/python-ucs4/bin/easy_install pip \
    && /opt/python-ucs4/bin/pip install virtualenv \
    && rm -rf /src

WORKDIR /yaga

COPY app app
COPY apns apns
COPY requirements.txt requirements.txt
COPY package.json package.json
COPY Gemfile Gemfile
COPY Gemfile.lock Gemfile.lock
COPY Procfile Procfile
COPY Rakefile Rakefile
COPY .env .env

RUN find . -type d -name "__pycache__" -exec rm -rf {} + > /dev/null 2>&1 \
    && find . -type f -name "*.pyc" -exec rm -rf {} + > /dev/null 2>&1

RUN /opt/python-ucs4/bin/virtualenv env \
    && source env/bin/activate \
    && pip install -r requirements.txt \
    && rm -rf /root/.cache \
    && npm install \
    && rm -rf /root/.npm \
    && bundle install

ENV PORT 8000

EXPOSE 8000

RUN echo '#!/usr/bin/env bash' > entrypoint.sh \
    && echo 'source env/bin/activate' >> entrypoint.sh \
    && echo 'exec "$@"' >> entrypoint.sh \
    && chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["bash"]

# docker rm $(docker ps -a -q)
# docker rmi $(docker images -q)
# docker build -t yaga:$(date '+%s') .
# docker run --name celery_worker_1 -d -i -t yaga:latest foreman start celery_worker
