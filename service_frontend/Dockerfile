FROM node:18-alpine as build

WORKDIR /app

COPY service_frontend/app/package*.json ./

RUN npm ci

COPY service_frontend/app ./

RUN npm run build

# nginx
FROM nginx:alpine

COPY service_frontend/app/nginx.conf.template /etc/nginx/templates/default.conf.template

RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/src/html/ /usr/share/nginx/html/
COPY --from=build /app/dist/ts/ /usr/share/nginx/html/js/
COPY --from=build /app/src/css/ /usr/share/nginx/html/css/

EXPOSE 80