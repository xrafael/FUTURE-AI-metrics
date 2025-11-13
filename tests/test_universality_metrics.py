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
        
        # Use the new format with metadata (matching the actual config structure)
        config = {
            "workflow_requirements": [
                {
                    "name": "hardware_type",
                    "data_type": "string",
                    "possible_values": ["cpu", "gpu"],
                    "required": True,
                    "description": "Type of hardware required (CPU or GPU)"
                },
                {
                    "name": "ram_memory",
                    "data_type": "number",
                    "min": 0,
                    "required": True,
                    "description": "RAM memory amount in GB (must be greater than 0)"
                },
                {
                    "name": "disk_space",
                    "data_type": "number",
                    "min": 0,
                    "required": True,
                    "description": "Hard disk space needed in GB (must be greater than 0)"
                },
                {
                    "name": "operating_system",
                    "data_type": "string",
                    "required": True,
                    "description": "Operating system name and version"
                },
                {
                    "name": "libraries",
                    "data_type": "list",
                    "item_type": "string",
                    "min_items": 1,
                    "required": True,
                    "description": "List of required library/dependency names"
                },
                {
                    "name": "preprocessing_algorithms",
                    "data_type": "list",
                    "item_type": "string",
                    "min_items": 1,
                    "required": True,
                    "description": "List of preprocessing algorithm names"
                }
            ],
            "compatibility_categories": [
                {
                    "name": "scanner_manufacturer",
                    "data_type": "string",
                    "required": True,
                    "description": "Scanner manufacturer name"
                },
                {
                    "name": "scanner_model",
                    "data_type": "string",
                    "required": True,
                    "description": "Specific scanner model name"
                },
                {
                    "name": "reconstruction_algorithms",
                    "data_type": "list",
                    "item_type": "string",
                    "min_items": 1,
                    "required": True,
                    "description": "List of supported reconstruction algorithm names"
                },
                {
                    "name": "post_processing_algorithms",
                    "data_type": "list",
                    "item_type": "string",
                    "min_items": 1,
                    "required": True,
                    "description": "List of supported post-processing algorithm names"
                },
                {
                    "name": "software_version",
                    "data_type": "string",
                    "required": True,
                    "description": "Version of the reconstruction software"
                },
                {
                    "name": "image_format",
                    "data_type": "string_or_list",
                    "item_type": "string",
                    "min_items": 1,
                    "required": True,
                    "description": "Supported image format(s)"
                },
                {
                    "name": "acquisition_parameters",
                    "data_type": "dict_or_list",
                    "required": True,
                    "description": "Supported acquisition parameters"
                }
            ],
            "operational_medical_sites_categories": [
                {
                    "name": "department",
                    "data_type": "string",
                    "required": True,
                    "description": "Department name where the AI tool will be used"
                },
                {
                    "name": "section",
                    "data_type": "string",
                    "required": True,
                    "description": "Section name within the department"
                },
                {
                    "name": "specialty",
                    "data_type": "string",
                    "required": True,
                    "description": "Medical specialty"
                },
                {
                    "name": "clinical_site_type",
                    "data_type": "string",
                    "required": True,
                    "description": "Type of clinical site"
                }
            ],
            "operational_countries_categories": [
                {
                    "name": "countries",
                    "data_type": "list",
                    "item_type": "string",
                    "min_items": 1,
                    "required": True,
                    "description": "List of countries for which the tool is designed"
                },
                {
                    "name": "regulations",
                    "data_type": "list",
                    "item_type": "string",
                    "min_items": 1,
                    "required": True,
                    "description": "List of regulations and legal frameworks that apply"
                },
                {
                    "name": "legal_frameworks",
                    "data_type": "list",
                    "item_type": "string",
                    "min_items": 1,
                    "required": True,
                    "description": "List of legal frameworks and compliance standards"
                }
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_init_with_config(self):
        """Test initialization with custom config path."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        self.assertIsNotNone(metrics.workflow_requirements)
        self.assertIsNotNone(metrics.compatibility_categories)
        self.assertIsNotNone(metrics.operational_medical_sites_categories)
        self.assertIsNotNone(metrics.operational_countries_categories)
    
    def test_workflow_requirements_score_complete(self):
        """Test workflow requirements score with complete data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        user_requirements = {
            'hardware_type': 'gpu',
            'ram_memory': 16,
            'disk_space': 50,
            'operating_system': 'Linux Ubuntu 20.04',
            'libraries': ['tensorflow', 'numpy', 'pandas'],
            'preprocessing_algorithms': ['Normalization', 'Bias Field Correction']
        }
        
        result = metrics.workflow_requirements_score(user_requirements)
        
        self.assertEqual(result['completeness_score'], 1.0)
        self.assertEqual(result['validity_score'], 1.0)
        self.assertTrue(all(result['completeness_details'].values()))
        self.assertTrue(all(result['validity_details'].values()))
        self.assertEqual(len(result['missing']), 0)
        self.assertEqual(len(result['invalid']), 0)
    
    def test_workflow_requirements_score_partial(self):
        """Test workflow requirements score with partial data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        user_requirements = {
            'hardware_type': 'gpu',
            'ram_memory': 16,
            # Missing disk_space, operating_system, libraries, preprocessing_algorithms
        }
        
        result = metrics.workflow_requirements_score(user_requirements)
        
        self.assertLess(result['completeness_score'], 1.0)
        self.assertGreater(len(result['missing']), 0)
        # Validity score should also be less than 1.0 since missing fields are invalid
        self.assertLess(result['validity_score'], 1.0)
    
    def test_scanner_software_compatibility_complete(self):
        """Test scanner software compatibility with complete data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        compatibility_info = {
            'scanner_manufacturer': 'Siemens',
            'scanner_model': 'MAGNETOM Skyra',
            'reconstruction_algorithms': ['GRAPPA', 'SENSE'],
            'post_processing_algorithms': ['Noise Reduction', 'Edge Enhancement'],
            'software_version': 'VE11C',
            'image_format': ['DICOM', 'NIfTI'],
            'acquisition_parameters': {'field_strength': '3T'}
        }
        
        result = metrics.scanner_software_compatibility(compatibility_info)
        
        self.assertEqual(result['completeness_score'], 1.0)
        self.assertEqual(result['validity_score'], 1.0)
        self.assertTrue(all(result['completeness_details'].values()))
        self.assertTrue(all(result['validity_details'].values()))
        self.assertEqual(len(result['missing']), 0)
        self.assertEqual(len(result['invalid']), 0)
    
    def test_scanner_software_compatibility_partial(self):
        """Test scanner software compatibility with partial data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        compatibility_info = {
            'scanner_manufacturer': 'Siemens',
            'scanner_model': 'MAGNETOM Skyra',
            # Missing other fields
        }
        
        result = metrics.scanner_software_compatibility(compatibility_info)
        
        self.assertLess(result['completeness_score'], 1.0)
        self.assertGreater(len(result['missing']), 0)
        self.assertLess(result['validity_score'], 1.0)
    
    def test_operational_medical_sites_score_complete(self):
        """Test operational medical sites score with complete data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        medical_site_info = {
            'department': 'Radiology',
            'section': 'Neuroradiology',
            'specialty': 'Neuroradiology',
            'clinical_site_type': 'hospital'
        }
        
        result = metrics.operational_medical_sites_score(medical_site_info)
        
        self.assertEqual(result['completeness_score'], 1.0)
        self.assertEqual(result['validity_score'], 1.0)
        self.assertTrue(all(result['completeness_details'].values()))
        self.assertTrue(all(result['validity_details'].values()))
        self.assertEqual(len(result['missing']), 0)
        self.assertEqual(len(result['invalid']), 0)
    
    def test_operational_medical_sites_score_partial(self):
        """Test operational medical sites score with partial data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        medical_site_info = {
            'department': 'Radiology',
            'section': 'Neuroradiology',
            # Missing specialty and clinical_site_type
        }
        
        result = metrics.operational_medical_sites_score(medical_site_info)
        
        self.assertLess(result['completeness_score'], 1.0)
        self.assertGreater(len(result['missing']), 0)
        self.assertEqual(result['completeness_score'], 0.5)  # 2 out of 4 fields present
        self.assertLess(result['validity_score'], 1.0)
    
    def test_operational_countries_score_complete(self):
        """Test operational countries score with complete data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        countries_info = {
            'countries': ['USA', 'EU', 'UK'],
            'regulations': ['GDPR', 'FDA', 'MDR', 'HIPAA'],
            'legal_frameworks': ['EU MDR 2017/745', 'FDA 21 CFR Part 820']
        }
        
        result = metrics.operational_countries_score(countries_info)
        
        self.assertEqual(result['completeness_score'], 1.0)
        self.assertEqual(result['validity_score'], 1.0)
        self.assertTrue(all(result['completeness_details'].values()))
        self.assertTrue(all(result['validity_details'].values()))
        self.assertEqual(len(result['missing']), 0)
        self.assertEqual(len(result['invalid']), 0)
    
    def test_operational_countries_score_partial(self):
        """Test operational countries score with partial data."""
        metrics = UniversalityMetrics(config_path=self.config_path)
        
        countries_info = {
            'countries': ['USA', 'EU'],
            # Missing regulations and legal_frameworks
        }
        
        result = metrics.operational_countries_score(countries_info)
        
        self.assertLess(result['completeness_score'], 1.0)
        self.assertGreater(len(result['missing']), 0)
        self.assertLess(result['validity_score'], 1.0)


if __name__ == '__main__':
    unittest.main()

