FROM node:18-alpine as build

WORKDIR /app

COPY app/package*.json ./

RUN npm ci

COPY app .

RUN npm run build

# nginx
FROM nginx:alpine

COPY app/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80