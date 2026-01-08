# Mound Detection Variability Report
**Generated:** 2025-12-21 22:46:30

## 1. Base Model Variability (N=1)
_Performance stability of a single run, averaged across all iterations._

| Metric | Mean | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| **F1 Score** | 0.8856 | ±0.0412 | 0.8381 | 0.9423 |
| **Precision** | 0.8775 | ±0.0456 | 0.8148 | 0.9245 |
| **Recall** | 0.8941 | ±0.0407 | 0.8627 | 0.9608 |

### Per-Class Breakdown (N=1)
| Symbol Class | F1 Score | Precision | Recall |
| :--- | :--- | :--- | :--- |
| **burial_mound** | 0.8844 (±0.04) | 0.8647 | 0.9053 |
| **benchmark_mound** | 0.8769 (±0.05) | 0.8906 | 0.8667 |
| **triangulation_mound** | 0.6857 (±0.10) | 0.6500 | 0.7334 |

## 2. Consensus Strategy Analysis ('n of x')
_Simulation of voting strategies to improve stability and performance._

| Strategy (N/Votes) | Mean F1 | Mean Recall | Mean Prec | 95% CI | Min | Max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **5/2** 🏆 | **0.9143** | 0.9412 | 0.8889 | [0.914, 0.914] | 0.914 | 0.914 |
| **5/3** | **0.8602** | 0.7843 | 0.9524 | [0.860, 0.860] | 0.860 | 0.860 |
| **5/1** | **0.8099** | 0.9608 | 0.7000 | [0.810, 0.810] | 0.810 | 0.810 |
| **5/4** | **0.6216** | 0.4510 | 1.0000 | [0.622, 0.622] | 0.622 | 0.622 |
| **5/5** | **0.3548** | 0.2157 | 1.0000 | [0.355, 0.355] | 0.355 | 0.355 |

### Per-Class Consensus Breakdown
_Impact of consensus strategies on specific symbol types._

#### Strategy: 5/2
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.9367 | ±0.0000 |
| benchmark_mound | 0.8889 | ±0.0000 |
| triangulation_mound | 0.5714 | ±0.0000 |

#### Strategy: 5/3
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.8406 | ±0.0000 |
| benchmark_mound | 0.8889 | ±0.0000 |
| triangulation_mound | 0.8000 | ±0.0000 |

#### Strategy: 5/1
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.8132 | ±0.0000 |
| benchmark_mound | 0.8000 | ±0.0000 |
| triangulation_mound | 0.6000 | ±0.0000 |

#### Strategy: 5/4
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.5556 | ±0.0000 |
| benchmark_mound | 0.7143 | ±0.0000 |
| triangulation_mound | 0.8000 | ±0.0000 |

#### Strategy: 5/5
| Symbol | Mean F1 | Std Dev |
| :--- | :--- | :--- |
| burial_mound | 0.2667 | ±0.0000 |
| benchmark_mound | 0.5000 | ±0.0000 |
| triangulation_mound | 0.5000 | ±0.0000 |

