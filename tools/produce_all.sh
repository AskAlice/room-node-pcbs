#!/bin/bash
# Produce all KiCad-rendered assets + fab outputs for every board.
# Requires: kicad-cli 10 (set KICAD_CLI env or /tmp/squashfs-root/bin/kicad-cli)
set -u
KC="${KICAD_CLI:-/tmp/squashfs-root/bin/kicad-cli}"
cd /mnt/agents/output/room-node-pcbs
mkdir -p renders fab
for b in roomnode-s3 roomnode-c6 roomnode-c3-mini airnode-s3; do
  pcb=boards/$b/$b.kicad_pcb
  sch=boards/$b/$b.kicad_sch
  echo "===== $b"
  # raytraced 3D renders (top perspective with floor, bottom)
  $KC pcb render -o renders/${b}_kicad3d.png -w 1400 -h 1050 --side top --quality high --floor --perspective "$pcb" 2>&1 | tail -1
  $KC pcb render -o renders/${b}_kicad3d_bottom.png -w 1400 -h 1050 --side bottom --quality high "$pcb" 2>&1 | tail -1
  # routing screenshot (2D SVG of copper+mask+silk)
  $KC pcb export svg -o renders/${b}_routing.svg --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,Edge.Cuts "$pcb" 2>&1 | tail -1
  # schematic screenshot
  $KC sch export svg -o renders/${b}_schematic.svg "$sch" 2>&1 | tail -1
  $KC sch export pdf -o renders/${b}_schematic.pdf "$sch" 2>&1 | tail -1
  # fab package: gerbers + drill + pick&place + bom
  f=fab/$b
  mkdir -p "$f"
  $KC pcb export gerbers -o "$f/" "$pcb" 2>&1 | tail -1
  $KC pcb export drill -o "$f/" "$pcb" 2>&1 | tail -1
  $KC pcb export pos --format csv --units mm -o "$f/${b}_pos.csv" "$pcb" 2>&1 | tail -1
  $KC sch export bom -o "$f/${b}_bom.csv" "$sch" 2>&1 | tail -1
  (cd "$f" && zip -q -9 ../${b}_jlcpcb.zip ./* )
  echo "zip: fab/${b}_jlcpcb.zip"
done
echo DONE
