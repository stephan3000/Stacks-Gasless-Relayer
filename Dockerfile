# Build Stage
FROM rust:1.88-slim-bookworm as builder

WORKDIR /usr/src/app

# Install build dependencies (openssl)
RUN apt-get update && apt-get install -y pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

# Copy manifests
COPY Cargo.toml Cargo.lock ./

# Create dummy src to cache dependencies
RUN mkdir src && \
    echo "fn main() {println!(\"if you see this, the build broke\")}" > src/main.rs && \
    echo "pub fn dummy() {}" > src/lib.rs

# Build dependencies
RUN cargo build --release

# Remove dummy source
RUN rm -rf src

# Copy actual source code
COPY . .

# Build actual application
# Touch main.rs to force rebuild
RUN touch src/main.rs && cargo build --release

# Runtime Stage
FROM debian:bookworm-slim

WORKDIR /usr/local/bin

# Install runtime dependencies
RUN apt-get update && apt-get install -y libssl3 ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy binary from builder
COPY --from=builder /usr/src/app/target/release/openzeppelin-relayer ./relayer

# Copy configuration templates
COPY --from=builder /usr/src/app/config ./config

# Create config directory
RUN mkdir -p config

# Expose port
EXPOSE 8080

CMD ["./relayer"]
