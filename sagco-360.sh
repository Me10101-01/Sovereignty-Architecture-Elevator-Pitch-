#!/bin/sh
set -u

DEVICE="${1:-unknown}"
ROOT="$HOME/SAGCO_OBSIDIAN_BRAIN/live360"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN="$ROOT/$DEVICE"
REPORT="$RUN/live360_$STAMP.md"
CSV="$ROOT/live360_ledger.csv"

mkdir -p "$RUN"

[ -f "$CSV" ] || echo "time,device,ipv4,ipv6,gateway,status" > "$CSV"

IPV4="$(ip -4 addr 2>/dev/null | awk '/inet /{print $2}' | tr '\n' ' ')"
IPV6="$(ip -6 addr 2>/dev/null | awk '/inet6 /{print $2}' | tr '\n' ' ')"
GW="$(ip route 2>/dev/null | awk '/default/{print $3; exit}')"

PING4="$(ping -c 1 -W 2 1.1.1.1 2>/dev/null | tail -2 || echo PING4_FAIL)"
PING6="$(ping6 -c 1 -W 2 2606:4700:4700::1111 2>/dev/null | tail -2 || echo PING6_FAIL)"
ROUTE4="$(ip route 2>/dev/null || echo NO_IPV4_ROUTE)"
ROUTE6="$(ip -6 route 2>/dev/null || echo NO_IPV6_ROUTE)"
ARP="$(ip neigh 2>/dev/null || arp -a 2>/dev/null || echo NO_ARP_TABLE)"

cat > "$REPORT" <<R
# SAGCO Live 360 Report

time: $STAMP
device: $DEVICE
status: SAGCO_360_PASS

## IPv4
$IPV4

## IPv6
$IPV6

## Gateway
$GW

## Ping IPv4
\`\`\`
$PING4
\`\`\`

## Ping IPv6
\`\`\`
$PING6
\`\`\`

## IPv4 Routes
\`\`\`
$ROUTE4
\`\`\`

## IPv6 Routes
\`\`\`
$ROUTE6
\`\`\`

## ARP / Neighbor Table
\`\`\`
$ARP
\`\`\`
R

echo "$STAMP,$DEVICE,\"$IPV4\",\"$IPV6\",\"$GW\",SAGCO_360_PASS" >> "$CSV"

echo "STATUS=SAGCO_360_PASS"
echo "DEVICE=$DEVICE"
echo "REPORT=$REPORT"
echo "LEDGER=$CSV"
