FROM node:20-alpine AS base
WORKDIR /repo
RUN npm install -g yarn@1.22.22

FROM base AS deps
COPY package.json ./
COPY apps/frontend/package.json apps/frontend/package.json
RUN yarn install

FROM deps AS dev
COPY . .
WORKDIR /repo/apps/frontend
CMD ["yarn", "dev", "--host", "0.0.0.0", "--port", "5173"]

FROM deps AS build
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
