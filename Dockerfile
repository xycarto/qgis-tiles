ARG ubuntu_dist=jammy

FROM ubuntu:${ubuntu_dist}

ARG ubuntu_dist
ARG repo=debian

RUN apt update && apt install -y gnupg wget software-properties-common && \
    wget -qO - https://qgis.org/downloads/qgis-2022.gpg.key | gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/qgis-archive.gpg --import && \
    chmod a+r /etc/apt/trusted.gpg.d/qgis-archive.gpg && \
    add-apt-repository "deb https://qgis.org/${repo} ${ubuntu_dist} main" && \
    apt update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y qgis python3-qgis python3-qgis-common \
      python3-pytest python3-mock xvfb && \
    apt-get clean

RUN apt-get -y update && apt-get install -y curl make gnupg2 pkg-config openssl libssl-dev

RUN apt update && apt install -y libgdal-dev

# RUN wget http://nz2.archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.17_amd64.deb

# RUN dpkg -i libssl1.1_1.1.1f-1ubuntu2.17_amd64.deb

RUN apt-get -y update && apt-get install -y openssl

RUN apt update && curl -O -L https://github.com/t-rex-tileserver/t-rex/releases/download/v0.14.3/t-rex-v0.14.3-x86_64-linux-gnu.tar.gz && tar xf t-rex-v0.14.3-x86_64-linux-gnu.tar.gz -C /usr/local/bin

RUN apt-get -y install python3-pip

RUN pip3 install --upgrade pip

RUN pip3 install geopandas pandas rasterio tomli_w

RUN apt-get install -y postgresql-client

RUN pip install morecantile rio_tiler jenkspy awscli

RUN apt-get update && apt-get -y install postgresql postgresql-contrib

RUN apt-get update && apt-get -y install postgis

# Update the database settings
# USER postgres
RUN sed -i 's/md5\|peer/trust/' /etc/postgresql/14/main/pg_hba.conf
RUN sed -i -e 's/# en_NZ.UTF-8 UTF-8/en_NZ.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
RUN sed -i 's/C.UTF-8/en_NZ.UTF-8/' /etc/postgresql/14/main/postgresql.conf

RUN apt install -y jq

RUN apt update && apt install -y nodejs npm
RUN npm install -g n
RUN n stable
RUN npm install -g npm@latest
RUN npm cache clean --force

RUN mkdir /.npm
RUN chmod ugo+w /.npm

ENV QT_QPA_PLATFORM=offscreen