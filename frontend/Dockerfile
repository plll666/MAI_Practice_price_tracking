# frontend/Dockerfile
FROM node:20-alpine as builder

WORKDIR /app

# Копируем package files
COPY package*.json ./
RUN npm install

# Копируем исходники
COPY . .

# Собираем приложение
RUN npm run build

# Production stage
FROM nginx:alpine

# Копируем конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные файлы
COPY --from=builder /app/dist /usr/share/nginx/html

# Проверяем что index.html существует
RUN ls -la /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]