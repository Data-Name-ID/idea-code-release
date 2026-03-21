FROM node:20-alpine AS base
WORKDIR /repo
COPY package.json yarn.lock ./
COPY apps/frontend/package.json apps/frontend/package.json
RUN yarn install --frozen-lockfile

FROM base AS build
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
COPY . .
WORKDIR /repo/apps/frontend
RUN yarn build

FROM nginx:1.27-alpine AS prod
COPY apps/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /repo/apps/frontend/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
