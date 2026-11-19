# Build stage
FROM --platform=$BUILDPLATFORM node:22-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# @vmscloud 패키지는 public npm 에서 받으므로 레지스트리 인증이 필요 없다.
RUN echo "shamefully-hoist=true" > .npmrc && \
    pnpm install --no-frozen-lockfile

COPY . .
RUN pnpm build

# Production stage
FROM nginx:stable-alpine

# Enforce the security floor even when a different stable image is published.
RUN set -eu; \
    actual="$(nginx -v 2>&1)"; \
    version="${actual#nginx version: nginx/}"; \
    printf '%s\n' "$version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; \
    comparison="$(apk version -t "$version" 1.30.7)"; \
    case "$comparison" in '='|'>') ;; *) echo "NGINX $version is below 1.30.7" >&2; exit 1 ;; esac; \
    printf 'NGINX_BASE nginx=%s minimum=1.30.7 result=PASS\n' "$version"


COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]