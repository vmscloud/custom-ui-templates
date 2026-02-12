# Build stage
FROM --platform=$BUILDPLATFORM node:22-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml ./

# 🔥 GitHub Packages 인증 추가
RUN --mount=type=secret,id=npm_token \
    echo "@vmscloud:registry=https://npm.pkg.github.com/" > .npmrc && \
    echo "//npm.pkg.github.com/:_authToken=$(cat /run/secrets/npm_token)" >> .npmrc && \
    pnpm install --frozen-lockfile && \
    rm -f .npmrc

COPY . .
RUN node scripts/license.js
RUN pnpm build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]