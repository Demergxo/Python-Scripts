FROM golang:1.7.3 as builder
WORKDIR /go/src/github.com/alexellis/href-counter/
RUN go install golang.org/x/net/html
COPY app.go .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /go/src/github.com/alexellis/href-counter/app .
COPY --from=nginx:latest /etc/nginx/nginx.conf /nginx.conf
CMD ["./app"]


FROM golang:1.21 as builder

WORKDIR /app

# Copia el código fuente
COPY app.go .

# Inicializa módulos y descarga dependencias
RUN go mod init href-counter && \
    go get golang.org/x/net/html

# Compila el binario
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

# Imagen final minimalista
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/app .
COPY --from=nginx:latest /etc/nginx/nginx.conf /nginx.conf

CMD ["./app"]
