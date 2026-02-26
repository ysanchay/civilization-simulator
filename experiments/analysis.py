"""Statistical analysis utilities."""

from typing import List, Dict, Any, Tuple
import math


class StatisticalAnalyzer:
    """Statistical analysis for experiment results."""
    
    @staticmethod
    def mean(values: List[float]) -> float:
        """Calculate mean."""
        if not values:
            return 0
        return sum(values) / len(values)
    
    @staticmethod
    def std(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0
        m = StatisticalAnalyzer.mean(values)
        return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))
    
    @staticmethod
    def median(values: List[float]) -> float:
        """Calculate median."""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        return sorted_values[n // 2]
    
    @staticmethod
    def t_test(sample1: List[float], sample2: List[float]) -> Tuple[float, float]:
        """
        Perform independent t-test.
        
        Returns:
            Tuple of (t-statistic, approximate p-value)
        """
        n1, n2 = len(sample1), len(sample2)
        if n1 < 2 or n2 < 2:
            return 0, 1.0
        
        m1, m2 = StatisticalAnalyzer.mean(sample1), StatisticalAnalyzer.mean(sample2)
        s1, s2 = StatisticalAnalyzer.std(sample1), StatisticalAnalyzer.std(sample2)
        
        # Pooled standard error
        se = math.sqrt((s1 ** 2 / n1) + (s2 ** 2 / n2))
        
        if se == 0:
            return 0, 1.0
        
        t = (m1 - m2) / se
        
        # Approximate p-value using normal distribution
        # (proper implementation would use t-distribution)
        p = 2 * (1 - StatisticalAnalyzer._normal_cdf(abs(t)))
        
        return t, p
    
    @staticmethod
    def _normal_cdf(x: float) -> float:
        """Approximate normal CDF."""
        # Approximation using error function
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    @staticmethod
    def effect_size(sample1: List[float], sample2: List[float]) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(sample1), len(sample2)
        if n1 < 2 or n2 < 2:
            return 0
        
        m1, m2 = StatisticalAnalyzer.mean(sample1), StatisticalAnalyzer.mean(sample2)
        s1, s2 = StatisticalAnalyzer.std(sample1), StatisticalAnalyzer.std(sample2)
        
        # Pooled standard deviation
        pooled_std = math.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0
        
        return (m1 - m2) / pooled_std
    
    @staticmethod
    def compare_experiments(
        results1: Dict[str, List[float]],
        results2: Dict[str, List[float]],
        alpha: float = 0.05,
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare two experiments.
        
        Returns:
            Dictionary of metric -> comparison results
        """
        comparisons = {}
        
        all_metrics = set(results1.keys()) | set(results2.keys())
        
        for metric in all_metrics:
            sample1 = results1.get(metric, [])
            sample2 = results2.get(metric, [])
            
            if not sample1 or not sample2:
                continue
            
            t, p = StatisticalAnalyzer.t_test(sample1, sample2)
            d = StatisticalAnalyzer.effect_size(sample1, sample2)
            
            comparisons[metric] = {
                'mean1': StatisticalAnalyzer.mean(sample1),
                'mean2': StatisticalAnalyzer.mean(sample2),
                'std1': StatisticalAnalyzer.std(sample1),
                'std2': StatisticalAnalyzer.std(sample2),
                't_statistic': t,
                'p_value': p,
                'effect_size': d,
                'significant': p < alpha,
            }
        
        return comparisons
    
    @staticmethod
    def confidence_interval(
        values: List[float],
        confidence: float = 0.95,
    ) -> Tuple[float, float]:
        """Calculate confidence interval."""
        if len(values) < 2:
            m = StatisticalAnalyzer.mean(values)
            return (m, m)
        
        m = StatisticalAnalyzer.mean(values)
        s = StatisticalAnalyzer.std(values)
        n = len(values)
        
        # z-score for confidence level
        z = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(confidence, 1.96)
        
        margin = z * s / math.sqrt(n)
        
        return (m - margin, m + margin)