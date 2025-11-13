"""
Tests for UniversalityMetrics class.
"""

import unittest
import os
import sys
import json
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from future_ai_metrics.universality.metrics import UniversalityMetrics


class TestUniversalityMetrics(unittest.TestCase):
    """Test cases for UniversalityMetrics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.json')
        
        config = {
            "real_requirements": [
                "hardware_type",
                "ram_memory",
                "disk_space",
                "operating_system",
                "libraries"
            ],
            "compatibility_categories": [
                "scanner_manufacturer",
                "scanner_model",
                "reconstruction_algorithms",
                "software_version",
                "image_format",
                "acquisition_parameters"
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_config(self):
        """Test initialization with custom config path."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        self.assertIsNotNone(metrics.real_requirements)
        self.assertIsNotNone(metrics.compatibility_categories)
    
    def test_workflow_requirements_score_complete(self):
        """Test workflow requirements score with complete data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        user_requirements = {
            'hardware_type': 'gpu',
            'ram_memory': 16,
            'disk_space': 50,
            'operating_system': 'Linux Ubuntu 20.04',
            'libraries': ['tensorflow', 'numpy', 'pandas']
        }
        
        result = metrics.workflow_requirements_score(user_requirements)
        
        self.assertEqual(result['score'], 1.0)
        self.assertTrue(all(result['details'].values()))
        self.assertEqual(len(result['missing']), 0)
    
    def test_workflow_requirements_score_partial(self):
        """Test workflow requirements score with partial data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        user_requirements = {
            'hardware_type': 'gpu',
            'ram_memory': 16,
            # Missing disk_space, operating_system, libraries
        }
        
        result = metrics.workflow_requirements_score(user_requirements)
        
        self.assertLess(result['score'], 1.0)
        self.assertGreater(len(result['missing']), 0)
    
    def test_scanner_software_compatibility_complete(self):
        """Test scanner software compatibility with complete data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        compatibility_info = {
            'scanner_manufacturer': 'Siemens',
            'scanner_model': 'MAGNETOM Skyra',
            'reconstruction_algorithms': ['GRAPPA', 'SENSE'],
            'software_version': 'VE11C',
            'image_format': ['DICOM', 'NIfTI'],
            'acquisition_parameters': {'field_strength': '3T'}
        }
        
        result = metrics.scanner_software_compatibility(compatibility_info)
        
        self.assertEqual(result['score'], 1.0)
        self.assertTrue(all(result['details'].values()))
        self.assertEqual(len(result['missing']), 0)
    
    def test_scanner_software_compatibility_partial(self):
        """Test scanner software compatibility with partial data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        compatibility_info = {
            'scanner_manufacturer': 'Siemens',
            'scanner_model': 'MAGNETOM Skyra',
            # Missing other fields
        }
        
        result = metrics.scanner_software_compatibility(compatibility_info)
        
        self.assertLess(result['score'], 1.0)
        self.assertGreater(len(result['missing']), 0)


if __name__ == '__main__':
    unittest.main()

