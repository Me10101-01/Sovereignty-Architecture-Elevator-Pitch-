CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -O2 -Isrc -D_POSIX_C_SOURCE=200809L
LDFLAGS = -lm

BIN  = sagco
BIN2 = exchanger_locator

# ── Main organism binary ────────────────────────────────────────────────────────
SRCS = \
    src/main.c \
    src/lexer/token_lexer.c \
    src/parser/ast_builder.c \
    src/parser/evidence_parser.c \
    src/router/dispatch.c \
    src/router/route_table.c \
    src/router/router.c \
    src/gps/bearing.c \
    src/field/insulation.c \
    src/ledger/receipt.c \
    src/ledger/seal.c \
    src/ledger/sha256.c \
    src/physics/ohm.c \
    src/network/curl.c \
    src/ninja/print_bridge.c

OBJS = $(SRCS:.c=.o)

# ── Standalone exchanger locator ─────────────────────────────────────────────────
LOCATOR_SRC = src/gps/exchanger_locator.c

all: $(BIN) $(BIN2)

$(BIN): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(BIN2): $(LOCATOR_SRC)
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

# ── Field test targets ───────────────────────────────────────────────────────────
test-insulation: $(BIN)
	@mkdir -p logs
	./$(BIN) field insulation --csv data/insulation_survey_ca1648j.csv

test-pipe: $(BIN)
	@mkdir -p logs
	./$(BIN) field pipe-survey --csv data/pipe_survey_ca1648j.csv

test-locator: $(BIN2)
	./$(BIN2) data/sample_readings.csv data/asset_fingerprints.json

test-bearing: $(BIN)
	@mkdir -p logs
	./$(BIN) gps bearing \
		--lat1 27.810164 --lon1 -97.593503 \
		--lat2 27.810203 --lon2 -97.593470

# ── Hydra — run all heads sequentially ──────────────────────────────────────────
hydra: all
	@echo ""
	@echo "  ╔══════════════════════════════════════════════════════════╗"
	@echo "  ║   SAGCO ORGANISM — HYDRA MODE — ALL HEADS                ║"
	@echo "  ╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@mkdir -p logs
	@echo "  [HEAD 1] exchanger_locator — magnetic fingerprint"
	@./$(BIN2) data/sample_readings.csv data/asset_fingerprints.json
	@echo "  [HEAD 2] field insulation — CA-1648 J coverage"
	@./$(BIN) field insulation --csv data/insulation_survey_ca1648j.csv
	@echo "  [HEAD 3] field pipe-survey — CA-1648 J weld inventory"
	@./$(BIN) field pipe-survey --csv data/pipe_survey_ca1648j.csv
	@echo "  [HEAD 4] gps bearing — node-to-node"
	@./$(BIN) gps bearing --lat1 27.810164 --lon1 -97.593503 --lat2 27.810203 --lon2 -97.593470
	@echo "  ══ HYDRA COMPLETE ══"
	@echo ""

# ── Package headless tar.gz ──────────────────────────────────────────────────────
tarball: all
	@./scripts/build-hydra.sh

# ── Install on Raspberry Pi ──────────────────────────────────────────────────────
install-pi:
	@./scripts/install-pi.sh

clean:
	rm -f $(OBJS) $(BIN) $(BIN2)
	rm -f sagco-hydra-*.tar.gz

.PHONY: all hydra tarball install-pi clean \
        test-insulation test-pipe test-locator test-bearing
