import unittest
import numpy as np
from my_pkg.lib import get_numpy_stats

class TestGetNumpyStats(unittest.TestCase):
    
    def test_get_numpy_stats(self):
        # Test with a simple list of numbers
        data = [1, 2, 3, 4, 5]
        result = get_numpy_stats(data)
        
        # Check if all expected keys are present
        self.assertIn('mean', result)
        self.assertIn('sum', result)
        self.assertIn('max', result)
        self.assertIn('min', result)
        self.assertIn('std', result)
        
        # Check if the values are correct
        self.assertEqual(result['mean'], 3.0)
        self.assertEqual(result['sum'], 15)
        self.assertEqual(result['max'], 5)
        self.assertEqual(result['min'], 1)
        self.assertAlmostEqual(result['std'], np.std(data))
        
    def test_empty_array(self):
        # Test with an empty array
        with self.assertRaises(ValueError):
            get_numpy_stats([])
            
    def test_with_numpy_array(self):
        # Test with a numpy array directly
        data = np.array([10, 20, 30, 40, 50])
        result = get_numpy_stats(data)
        
        self.assertEqual(result['mean'], 30.0)
        self.assertEqual(result['sum'], 150)
        self.assertEqual(result['max'], 50)
        self.assertEqual(result['min'], 10)
        self.assertAlmostEqual(result['std'], np.std(data))

if __name__ == '__main__':
    unittest.main()

