FROM debian

# Install required stuff
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y python3-pip python3 postgresql

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Setup PostgreSQL
USER postgres

# Allow local connections
RUN rm /etc/postgresql/11/main/pg_hba.conf && touch /etc/postgresql/11/main/pg_hba.conf
RUN echo 'local     all     all                 trust' >> /etc/postgresql/11/main/pg_hba.conf &&\
	echo 'host      all     all     0.0.0.0/0   trust' >> /etc/postgresql/11/main/pg_hba.conf &&\
	echo 'host      all     all     ::/0        trust' >> /etc/postgresql/11/main/pg_hba.conf

RUN echo "listen_addresses='*'" >> /etc/postgresql/11/main/postgresql.conf

COPY . /app

RUN service postgresql start &&\
	psql --command "CREATE USER tipuser WITH SUPERUSER PASSWORD 'tippass'" &&\
	createdb -O tipuser avengers &&\
	psql -d avengers --command "CREATE SCHEMA avengers_admin; CREATE SCHEMA avengers_coins; CREATE SCHEMA avengers_comments; CREATE SCHEMA avengers_main; CREATE SCHEMA avengers_msg; CREATE SCHEMA avengers_post; CREATE SCHEMA avengers_promotion; CREATE SCHEMA avengers_subforum; CREATE SCHEMA avengers_tips; CREATE SCHEMA avengers_user; CREATE SCHEMA avengers_user_business; CREATE SCHEMA avengers_wallet_bch; CREATE SCHEMA avengers_wallet_bch_test; CREATE SCHEMA avengers_wallet_btc; CREATE SCHEMA avengers_wallet_btc_test; CREATE SCHEMA avengers_wallet_monero; CREATE SCHEMA avengers_wallet_monero_stagenet; CREATE SCHEMA avengers_wallet_monero_testnet" &&\
	python3 startup.py &&\
	service postgresql stop
EXPOSE 5432
VOLUME ['/etc/postgresql', '/var/log/postgresql', '/var/lib/postgresql']

# Copy entire app into container
USER root

RUN printf "database_connection='postgresql://tipuser:tippass@localhost:5432/avengers'\nmailuser='mailuser'\nmailpass='mailpass'\nsecretkey='debugk'\nwtfkey='debugk'" > passwords.py

CMD service postgresql start && python3 runLan.py
