FROM mcr.microsoft.com/mssql/server:2022-latest

ENV ACCEPT_EULA=Y
ENV MSSQL_PID=Express

COPY ./init/init.sql /opt/mssql-tools/bin/init-db.sh
RUN chmod +x /opt/mssql-tools/bin/init-db.sh

EXPOSE 1433 