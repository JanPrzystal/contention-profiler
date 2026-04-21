import requests

PROM_URL = "http://145.100.131.48:30987/api/v1/query"

def query_median_latency(metric_name: str, profiling_time_s: int) -> float:
    """Query the median latency from a Prometheus histogram metric.
    
    Calculates the 0.5 quantile (median) of a histogram metric over a specified
    time window using Prometheus's histogram_quantile function.
    
    Args:
        metric_name: The name of the Prometheus histogram metric to query.
        profiling_time_s: The time window in seconds over which to calculate
            the rate and median latency.
    
    Returns:
        The median latency value as a float.
    
    Raises:
        requests.exceptions.HTTPError: If the HTTP request to Prometheus fails.
        Exception: If the query result does not contain exactly one result.
    """
    
    params = {
        "query": f"histogram_quantile(0.5, sum(rate({metric_name}[{profiling_time_s}s])) by (le))"
    }

    resp = requests.get(PROM_URL, params=params)
    resp.raise_for_status()   # raises if the request failed
    res = resp.json()['data']['result']
    if len(res) != 1:
        raise Exception("Result is of wrong size, should be of size 1")
    return float(res[0]['value'][1])