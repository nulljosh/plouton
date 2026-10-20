#!/bin/sh
# App Store product page header (the animated banner): 3840x1646, 21:9, 30 fps, 30 s, no audio.
# Talli's six glyphs (web/art/*.svg) engraved in scanlines on the grainy landing blue, drifting left
# one full row per loop so the end meets the start. Same look as the landing footer band.
# Run from the repo root: sh launch/make_banner.sh  ->  launch/banner/talli-header.mp4
set -e
W=3840 H=1646 CELL=1280 G=820 PITCH=14 LINE=6 SECS=30
OUT=launch/banner TMP=$(mktemp -d)
mkdir -p $OUT
BAND='#2F6FB0' INK='#a9cdef'

# One row of six glyph silhouettes, twice over, so a pan of one row loops.
for n in tally coins calendar envelope house mountain; do
  magick -background none -density 1200 web/art/$n.svg -resize ${G}x${G} -gravity center -extent ${CELL}x${H} $TMP/$n.png
done
magick $TMP/tally.png $TMP/coins.png $TMP/calendar.png $TMP/envelope.png $TMP/house.png $TMP/mountain.png +append $TMP/row.png
magick $TMP/row.png $TMP/row.png +append -alpha extract $TMP/mask.png
SW=$((CELL * 12))

# Rules: thick inside the glyphs, faint across the whole band.
magick -size 1x$PITCH xc:none -fill "$INK" -draw "rectangle 0,0 0,$((LINE - 1))" -write mpr:t +delete \
  -size ${SW}x$H tile:mpr:t $TMP/thick.png
magick -size 1x$PITCH xc:none -fill "$INK" -draw "rectangle 0,0 0,1" -write mpr:f +delete \
  -size ${SW}x$H tile:mpr:f -channel A -evaluate multiply 0.22 +channel $TMP/faint.png
magick $TMP/thick.png $TMP/mask.png -compose CopyOpacity -composite $TMP/glyphs.png
magick -size ${SW}x$H xc:"$BAND" $TMP/faint.png -composite $TMP/glyphs.png -composite $TMP/strip.png

ffmpeg -y -loglevel error -loop 1 -framerate 30 -i $TMP/strip.png -t $SECS \
  -vf "crop=$W:$H:'mod(t*$((CELL * 6))/$SECS,$((CELL * 6)))':0,noise=alls=10:allf=t,format=yuv420p" \
  -c:v libx264 -preset slow -crf 20 -maxrate 40M -bufsize 80M -profile:v high -movflags +faststart -an $OUT/talli-header.mp4
rm -rf $TMP
