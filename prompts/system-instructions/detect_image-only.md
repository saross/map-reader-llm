# Mound Detection (Image-Only)

Scan the Target Image. Mark all symbols that look like the Positive examples.

Return JSON with normalised coordinates (0-1000):

```json
{"detections": [{"box_2d": [ymin, xmin, ymax, xmax], "label": "mound"}]}
```
