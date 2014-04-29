Optimal Rebalancing Strategy using Dynamic Programming
------------------------------------------------------
This project is a Python implementation of the following MIT Working Paper:
'Optimal Rebalancing Strategy Using Dynamic Programming for Institutional Portfolios'
Authors: Walter Sun, Ayres Fan, Li-Wei Chen, Tom Schouwenaars, Marius A. Albota

Motivation & Model Description
------------------------------
Financial institutions generally employ fixed methods to rebalance portfolios, such as calendar basis or tolerance band triggers. In the proposed setup, the investor has a risk profile derived from a log wealth utility function. This utility function identifies the investor as a risk-averse individual; therefore the optimal portfolio, minimizing Variance can be calculated using Mean Variance Optimization.

Assuming a portfolio employs this optimal weight in period 0, the subsequent-in-time weights will drift due to the different returns in the assets. Standard strategies only take into account specific bounds for weight movements; once this threshold is reached, the portfolio is rebalanced to the optimal portfolio (the weight that minimizes Variance). The shortfall of these decisions is they do not account for costs related to the rebalancing. The strategy used in the literature, and replicated in the current application, makes rebalancing decisions dynamically, that is on the basis of transaction costs, sub-optimality costs and future costs in each period, for the whole sample.

Transaction costs of rebalancing are modeled linearly. Furthermore, not rebalancing leads to the portfolio deviating from the optimal portfolio, resulting in a lower utility for the investor. This leads to an increase in sub-optimality costs (i.e. the utility shortfall in comparison to having a perfectly balanced optimal portfolio – measured in bps). These are modeled using Certainty Equivalent Costs.

Finally, the rebalancing decision takes into account the future costs of rebalancing J_(t+1) (w_(t+1) ); this results in a dynamic model, characterized by the discrete-time Bellman Equation:

J_t^* (w_t )= 〖min〗_(u_t ) E[〖TC〗_(u_t )+ϵ_(u_t )+J_(t+1) (w_(t+1) )]