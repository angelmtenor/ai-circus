# Data Science & AI Notes  – Lessons from Experience


## 1. Learning & Reference Resources

### Courses & Tutorials

* [Applied Data Science with Python – University of Michigan](https://online.umich.edu/series/applied-data-science-with-python/)
* [Kaggle Learn](https://www.kaggle.com/learn/overview)
* [RAG Guide](https://www.promptingguide.ai/research/rag)

### Books

* **Deep Learning** (Goodfellow): [deeplearningbook.org](https://www.deeplearningbook.org/)
* **Deep Learning with Python** (Chollet)

### Online Guides

* [Google ML Guides](https://developers.google.com/machine-learning/guides/)
* [TutorialsPoint UNIX Quick Guide](https://www.tutorialspoint.com/unix/unix-quick-guide.htm)
* [VS Code Documentation](https://code.visualstudio.com/docs)
* [W3Schools](https://www.w3schools.com/)
* [Docker Install Guide](https://docs.docker.com/engine/install/ubuntu/)

---

## 2. Core DS / ML Concepts

### ML / DS Principles

* Start simple, establish baseline quickly
* Never touch test data during feature engineering
* Use stratified splits for imbalanced data
* Prefer permutation importance or SHAP over tree impurity importance
* Document all experiments, including failures

### ML Concepts

| Concept                   | Definition                                              |
| ------------------------- | ------------------------------------------------------- |
| **Supervised Learning**   | Predict output given input-output examples              |
| **Unsupervised Learning** | Derive structure from unlabeled data                    |
| **Feature Scaling**       | Normalize inputs for faster gradient descent            |
| **Regularization**        | Control model complexity (L1/L2) to prevent overfitting |
| **Overfitting**           | Fits training data but fails on new data                |
| **Underfitting**          | Model too simple; high bias                             |

### Train / Validation / Test Split

* Optimal: 60% train, 20% validation, 20% test
* Minimal: 70% train, 30% test

### Neural Networks

* Binary classification → Sigmoid
* ReLU networks → He initialization
* Batch normalization improves optimization
* Embeddings: `dimension ≈ √(possible_values)`
* Missing values → zero input

### Error Analysis

1. Start simple; test early on validation data
2. Plot learning curves
3. Manually analyze misclassified examples
4. Extract new features from error patterns

---

## 3. ML Workflow / Best Practices

### Data Handling

* Leakage prevention: hide test set; scale inside CV folds
* Imbalanced data: use F1, stratified splits, class_weight, oversample minorities
* Interpretability: SHAP, permutation importance, ablation studies

### Experimentation

* Monitor input features; version model configuration
* Document all experiments (including failures)
* Start simple, observe metrics, iterate

### Security & Credentials

* Keep credentials **outside** project repo
* Load keys from environment variables (use `cryptography` library)

```python
from cryptography.fernet import Fernet

key = os.getenv("ENCRYPTION_KEY")  # Never hardcode
cipher = Fernet(key)
decrypted = cipher.decrypt(encrypted_data)
```
