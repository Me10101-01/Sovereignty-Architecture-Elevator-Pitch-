# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM rust:1.78-slim AS builder

WORKDIR /build

# Copy only the manifest first so cargo can cache dependencies
COPY Cargo.toml ./

# Create a dummy main so cargo can pre-fetch deps
RUN mkdir src && echo 'fn main(){}' > src/main.rs && \
    echo 'pub mod units; pub mod voltage_divider; pub mod eru;' > src/lib.rs && \
    touch src/units.rs src/voltage_divider.rs src/eru.rs && \
    cargo build --release 2>/dev/null || true && \
    rm -rf src

# Now copy the real source
COPY src ./src

# Full release build
RUN cargo build --release --bin sagco-bias-core

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/target/release/sagco-bias-core /usr/local/bin/sagco-bias-core

# Non-root user
RUN useradd -m sagco
USER sagco

WORKDIR /home/sagco

ENTRYPOINT ["/usr/local/bin/sagco-bias-core"]
