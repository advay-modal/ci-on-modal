import numpy

def get_numpy_stats(data):
    """
    Calculate basic statistics on a numpy array.
    
    Args:
        data: A list or array-like object to convert to numpy array
        
    Returns:
        dict: A dictionary containing basic statistics (mean, sum, max, min, std)
    """
    arr = numpy.array(data)
    stats = {
        'mean': numpy.mean(arr),
        'sum': numpy.sum(arr),
        'max': numpy.max(arr),
        'min': numpy.min(arr),
        'std': numpy.std(arr)
    }
    return stats
