# Mound Detection Variability Report
**Generated:** 2025-12-20 17:18:10

## 1. Base Model Variability (N=1)
_Performance stability of a single run, averaged across all iterations._

| Metric | Mean | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| **F1 Score** | 0.6806 | ±0.0465 | 0.6316 | 0.7419 |
| **Precision** | 0.5781 | ±0.0578 | 0.5176 | 0.6479 |
| **Recall** | 0.8302 | ±0.0298 | 0.7925 | 0.8679 |

### Per-Class Breakdown (N=1)
| Symbol Class | F1 Score | Precision | Recall |
| :--- | :--- | :--- | :--- |
| **burial_mound** | 0.6854 (±0.07) | 0.5817 | 0.8421 |
| **benchmark_mound** | 0.0000 (±0.00) | 0.0000 | 0.0000 |
| **triangulation_mound** | 0.2495 (±0.11) | 0.1508 | 0.7333 |

## 2. Consensus Strategy Analysis ('n of x')
_Simulation of voting strategies to improve stability and performance._

| Strategy (N/Votes) | Mean F1 | Mean Recall | Mean Prec | 95% CI | Min | Max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **5/2** 🏆 | **0.8142** | 0.9020 | 0.7419 | [0.814, 0.814] | 0.814 | 0.814 |
| **5/3** | **0.6947** | 0.6471 | 0.7500 | [0.695, 0.695] | 0.695 | 0.695 |
| **5/4** | **0.5542** | 0.4510 | 0.7188 | [0.554, 0.554] | 0.554 | 0.554 |
| **5/1** | **0.4324** | 0.9412 | 0.2807 | [0.432, 0.432] | 0.432 | 0.432 |
| **5/5** | **0.3636** | 0.2353 | 0.8000 | [0.364, 0.364] | 0.364 | 0.364 |

### Per-Class Consensus Breakdown
_Impact of consensus strategies on specific symbol types._

#### Strategy: 5/2
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.8608 | ±0.0000 |
| benchmark_mound | 0.0000 | ±0.0000 |
| triangulation_mound | 0.3158 | ±0.0000 |

#### Strategy: 5/3
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.7385 | ±0.0000 |
| benchmark_mound | 0.0000 | ±0.0000 |
| triangulation_mound | 0.2667 | ±0.0000 |

#### Strategy: 5/4
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.5862 | ±0.0000 |
| benchmark_mound | 0.0000 | ±0.0000 |
| triangulation_mound | 0.1818 | ±0.0000 |

#### Strategy: 5/1
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.3933 | ±0.0000 |
| benchmark_mound | 0.0000 | ±0.0000 |
| triangulation_mound | 0.1818 | ±0.0000 |

#### Strategy: 5/5
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.4082 | ±0.0000 |
| benchmark_mound | 0.0000 | ±0.0000 |
| triangulation_mound | 0.2857 | ±0.0000 |

