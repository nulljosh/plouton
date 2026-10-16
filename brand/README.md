# Talli brand

Open `index.html` for the kit. `tokens.css` is the one source for colour, space, type and shape.

Talli Sans is drawn from stroke skeletons in `fonts/build.py`, with advance widths set per letter shape. Rebuild with `uv run --with fonttools --with shapely python fonts/build.py`, then copy the `.woff` to `web/fonts/`.
