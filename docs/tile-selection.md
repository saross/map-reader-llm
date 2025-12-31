# Tile Selection for Pre-Registration

This document records the training and holdout tile sets selected for the study.

## Selection Methodology

- **Selection date**: 2024-12-23
- **Random seed**: 1766464625
- **Samples per map**: 5 (balanced across 4 maps)
- **Maximum background**: 75% (tiles with >75% empty space excluded)
- **Adjacency distance**: 1 tile (spatial separation between training/holdout)
- **Tile size**: 448×448 pixels

## Training Tiles (n=20)

Tiles used for prompt development and few-shot examples.

### K-35-052-4_32635 (5 tiles)

| Tile ID | Mound Count | Density |
|---------|-------------|---------|
| K-35-052-4_32635_x1344_y2240.png | 2 | sparse |
| K-35-052-4_32635_x1792_y3136.png | 1 | sparse |
| K-35-052-4_32635_x3136_y3584.png | 0 | empty |
| K-35-052-4_32635_x3584_y3584.png | 3 | dense |
| K-35-052-4_32635_x896_y1792.png | 0 | empty |

### K-35-053-3_Elenovo (5 tiles)

| Tile ID | Mound Count | Density |
|---------|-------------|---------|
| K-35-053-3_Elenovo_x1792_y1792.png | 3 | dense |
| K-35-053-3_Elenovo_x1792_y896.png | 1 | sparse |
| K-35-053-3_Elenovo_x3136_y2688.png | 3 | dense |
| K-35-053-3_Elenovo_x3136_y3584.png | 2 | sparse |
| K-35-053-3_Elenovo_x3584_y1344.png | 0 | empty |

### K-35-062-2_Rakovski (5 tiles)

| Tile ID | Mound Count | Density |
|---------|-------------|---------|
| K-35-062-2_Rakovski_x1344_y1792.png | 2 | sparse |
| K-35-062-2_Rakovski_x1792_y2688.png | 0 | empty |
| K-35-062-2_Rakovski_x1792_y896.png | 3 | dense |
| K-35-062-2_Rakovski_x3136_y1792.png | 2 | sparse |
| K-35-062-2_Rakovski_x448_y2688.png | 3 | dense |

### K-35-078-1_Lesovo (5 tiles)

| Tile ID | Mound Count | Density |
|---------|-------------|---------|
| K-35-078-1_Lesovo_x1344_y0.png | 2 | sparse |
| K-35-078-1_Lesovo_x1344_y3136.png | 0 | empty |
| K-35-078-1_Lesovo_x2240_y2688.png | 0 | empty |
| K-35-078-1_Lesovo_x2688_y1344.png | 0 | empty |
| K-35-078-1_Lesovo_x448_y0.png | 0 | empty |

**Training set summary**: 20 tiles, 22 mounds total

---

## Holdout Tiles (n=20)

Tiles reserved for final evaluation. Spatially separated from training tiles.

### K-35-052-4_32635 (5 tiles)

| Tile ID | Mound Count | Density |
|---------|-------------|---------|
| K-35-052-4_32635_x0_y2688.png | 4 | dense |
| K-35-052-4_32635_x1792_y1344.png | 2 | sparse |
| K-35-052-4_32635_x3584_y0.png | 0 | empty |
| K-35-052-4_32635_x3584_y2240.png | 1 | sparse |
| K-35-052-4_32635_x448_y896.png | 0 | empty |

### K-35-053-3_Elenovo (5 tiles)

| Tile ID | Mound Count | Density |
|---------|-------------|---------|
| K-35-053-3_Elenovo_x2688_y1344.png | 0 | empty |
| K-35-053-3_Elenovo_x2688_y896.png | 1 | sparse |
| K-35-053-3_Elenovo_x448_y1792.png | 1 | sparse |
| K-35-053-3_Elenovo_x896_y0.png | 4 | dense |
| K-35-053-3_Elenovo_x896_y2240.png | 3 | dense |

### K-35-062-2_Rakovski (5 tiles)

| Tile ID | Mound Count | Density |
|---------|-------------|---------|
| K-35-062-2_Rakovski_x3584_y0.png | 0 | empty |
| K-35-062-2_Rakovski_x4032_y0.png | 2 | sparse |
| K-35-062-2_Rakovski_x4032_y1344.png | 3 | dense |
| K-35-062-2_Rakovski_x448_y1792.png | 2 | sparse |
| K-35-062-2_Rakovski_x448_y448.png | 3 | dense |

### K-35-078-1_Lesovo (5 tiles)

| Tile ID | Mound Count | Density |
|---------|-------------|---------|
| K-35-078-1_Lesovo_x1792_y1792.png | 0 | empty |
| K-35-078-1_Lesovo_x2688_y448.png | 2 | sparse |
| K-35-078-1_Lesovo_x3136_y3136.png | 0 | empty |
| K-35-078-1_Lesovo_x3584_y448.png | 0 | empty |
| K-35-078-1_Lesovo_x896_y896.png | 0 | empty |

**Holdout set summary**: 20 tiles, 28 mounds total

---

## Density Distribution

| Density | Training | Holdout |
|---------|----------|---------|
| Empty (0 mounds) | 8 | 8 |
| Sparse (1-2 mounds) | 7 | 7 |
| Dense (3+ mounds) | 5 | 5 |

---

## Source Files

- `inputs/training_manifest.json` - Training tile list
- `inputs/holdout_manifest.json` - Holdout tile list
- `inputs/tile_selection_metadata.json` - Full selection metadata
