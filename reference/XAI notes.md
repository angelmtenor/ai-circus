# **Guide to Machine Learning Explainability & Interpretability**

## **1. Explainability vs. Interpretability**

While often used interchangeably, these terms are distinct:

* **Interpretability:** The extent to which one can observe cause and effect in a system.
  *Intuition:* You understand how the model works mechanically, without necessarily knowing *why*.

* **Explainability:** The extent to which a model’s internal mechanics can be described in human terms.
  *Intuition:* You can explain *why* a model made a specific decision.

**Analogy:** A chemistry experiment is **interpretable** because you can see the process (mixing chemicals) and outcome (color change). It becomes **explainable** when you understand the molecular interactions behind the reaction.

---

## **2. Key Techniques for Model Inspection**

### **Feature Importance**

Measures each feature’s contribution to model predictions.

#### **A. Permutation Feature Importance (Model-Agnostic)**

*Steps:*
1. Train model and compute baseline score (accuracy, R², etc.).
2. Shuffle one feature’s values in validation data.
3. Recompute model score.
4. Difference from baseline = feature importance.

*Interpretation:* Large drop → feature is critical; small drop → feature less important.

**Caveat:** Correlated features can dilute importance. Solution: cluster correlated features and use one representative per cluster.

#### **B. Impurity-Based Importance**

*Default for tree models (e.g., Random Forest).* Can be biased toward high-cardinality features. Permutation importance is often more reliable.

---

## **3. Tools & Frameworks**

* **LIME:** Explains predictions locally by fitting a simple, interpretable model around a data point.
* **SHAP:** Game-theoretic approach providing consistent, locally accurate feature attributions.
* **ELI5:** Python library for inspecting and debugging ML models.
* **InterpretML:** Includes Explainable Boosting Machine (EBM), an interpretable GAM.

---

## **4. References & Resources**

**Reading**
* [KDnuggets: Explainability vs Interpretability](https://www.kdnuggets.com/2018/12/machine-learning-explainability-interpretability-ai.html)
* [Interpretable Machine Learning by Christoph Molnar](https://christophm.github.io/interpretable-ml-book/shap.html)
* [Ethical OS Principles](https://ethical.institute/principles.html#commitment-3)

**Tutorials & Guides**
* [Kaggle: Machine Learning Explainability](https://www.kaggle.com/learn/machine-learning-explainability)
* [Scikit-Learn: Permutation Importance](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html#sklearn.inspection.permutation_importance)
* [Handling Correlated Features](https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance.html)

**Libraries**
* [SHAP](https://github.com/slundberg/shap)
* [ELI5](https://github.com/TeamHG-Memex/eli5)
* [InterpretML](https://github.com/interpretml/interpret)
* [Awesome Production ML](https://github.com/EthicalML/awesome-production-machine-learning)
