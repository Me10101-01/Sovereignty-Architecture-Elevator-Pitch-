CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -O2 -Iinclude
LDFLAGS = -lm

SRCS = src/main.c src/holding.c src/portfolio.c src/calc.c src/report.c
OBJS = $(SRCS:.c=.o)
BIN  = divtrack

all: $(BIN)

$(BIN): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

# Seed portfolio with the recommended holdings
seed: $(BIN)
	./divtrack add SCHD  100  80.00  83.00  2.92 ROTH_IRA
	./divtrack add DGRO   50  55.00  57.00  1.26 TRAD_IRA
	./divtrack add VIG    25 190.00 195.00  3.12 TAXABLE
	./divtrack add JEPI   30  56.00  57.50  4.60 TAXABLE
	./divtrack update SCHD growth 0.10
	./divtrack update DGRO growth 0.09
	./divtrack update VIG  growth 0.07
	./divtrack update JEPI growth 0.00
	./divtrack

test: $(BIN)
	$(CC) $(CFLAGS) -o test_calc tests/test_calc.c src/holding.c src/portfolio.c src/calc.c src/report.c $(LDFLAGS)
	./test_calc

clean:
	rm -f $(OBJS) $(BIN) test_calc

.PHONY: all seed test clean
