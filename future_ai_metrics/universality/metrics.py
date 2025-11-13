"""
Machine Learning Metrics for Measuring Universality of Predictive Models.

This module provides a comprehensive set of metrics to evaluate how well
a predictive model generalizes across different domains, datasets, and conditions.
"""

from typing import Dict, List, Optional, Union
import json
import os


class UniversalityMetrics:
    """
    A class for computing metrics that measure the universality of predictive models.
    
    Universality refers to a model's ability to maintain performance across:
    - Different domains or datasets
    - Different data distributions
    - Different conditions or environments
    - Transfer learning scenarios
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the UniversalityMetrics class.
        
        Parameters
        ----------
        config_path : str, optional
            Path to the JSON configuration file containing both workflow requirements
            and scanner compatibility categories.
            If None, defaults to 'config/universality_metrics_config.json' in the project root directory.
        """
        # Get project root (parent of future_ai_metrics package)
        if config_path is None:
            # Get the directory where this module is located
            module_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to project root: future_ai_metrics/universality -> future_ai_metrics -> project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(module_dir)))
            config_path = os.path.join(project_root, 'config', 'universality_metrics_config.json')
        
        # Load configuration file
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.workflow_requirements = config.get('workflow_requirements', [])
                self.compatibility_categories = config.get('compatibility_categories', [])
                self.operational_medical_sites_categories = config.get('operational_medical_sites_categories', [])
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}. "
                "Please ensure the config/universality_metrics_config.json file exists in the project root."
            )
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in configuration file {config_path}: {e}"
            )
        
        if not self.workflow_requirements:
            raise ValueError(
                "No required categories found in configuration file. "
                "The 'workflow_requirements' key must contain a non-empty list."
            )
        
        if not self.compatibility_categories:
            raise ValueError(
                "No compatibility categories found in configuration file. "
                "The 'compatibility_categories' key must contain a non-empty list."
            )
        
        if not self.operational_medical_sites_categories:
            raise ValueError(
                "No operational medical sites categories found in configuration file. "
                "The 'operational_medical_sites_categories' key must contain a non-empty list."
            )
    
    def _validate_field(
        self,
        field_name: str,
        field_value: Union[str, int, float, List[str], Dict, None],
        field_type: Optional[str] = None
    ) -> bool:
        """
        Validate a field value based on its expected type and constraints.
        
        Parameters
        ----------
        field_name : str
            Name of the field being validated
        field_value : Union[str, int, float, List[str], Dict, None]
            The value to validate
        field_type : str, optional
            Special validation type (e.g., 'hardware_type' for CPU/GPU check)
            
        Returns
        -------
        bool
            True if the field is valid, False otherwise
        """
        if field_value is None:
            return False
        
        # Special validation for hardware_type
        if field_type == 'hardware_type':
            return (
                isinstance(field_value, str) and 
                field_value.lower() in ['cpu', 'gpu']
            )
        
        # Validation for numeric fields (int/float > 0)
        if field_type in ['ram_memory', 'disk_space']:
            return (
                isinstance(field_value, (int, float)) and 
                field_value > 0
            )
        
        # Validation for string fields (non-empty after strip)
        if isinstance(field_value, str):
            return len(field_value.strip()) > 0
        
        # Validation for list/tuple fields
        if isinstance(field_value, (list, tuple)):
            if len(field_value) == 0:
                return False
            # Check if all items are non-empty strings
            return all(
                isinstance(item, str) and len(item.strip()) > 0 
                for item in field_value
            )
        
        # Validation for dict fields (non-empty)
        if isinstance(field_value, dict):
            return len(field_value) > 0
        
        # For other types, consider valid if not None
        return True
    
    def workflow_requirements_score(
        self,
        user_requirements: Dict[str, Union[str, int, float, List[str], None]]
    ) -> Dict[str, Union[float, Dict[str, bool]]]:
        """
        Compute a metric that evaluates if the digital infrastructure settings
        for executing the AI tool are properly reported.
        
        This metric checks for the presence of:
        - Hardware type (CPU/GPU)
        - RAM memory amount
        - Hard disk space needed
        - Operating system appropriate
        - Required libraries/dependencies
        - Preprocessing algorithms
        
        Parameters
        ----------
        user_requirements : dict
            Dictionary containing infrastructure user_requirements. Expected keys:
            - 'hardware_type' (str): 'cpu' or 'gpu'
            - 'ram_memory' (int/float): RAM amount in GB
            - 'disk_space' (int/float): Hard disk space in GB
            - 'operating_system' (str): OS name/version
            - 'libraries' (list): List of required library names
            - 'preprocessing_algorithms' (list): List of preprocessing algorithm names
            
        Returns
        -------
        dict
            Dictionary containing:
            - 'score' (float): Completeness score between 0.0 and 1.0
            - 'details' (dict): Boolean flags for each requirement category
            - 'missing' (list): List of missing requirement categories
            
        """
        # Use required categories from instance variable (loaded from JSON)
        workflow_requirements = self.workflow_requirements
        
        # Check each category (only those defined in workflow_requirements)
        # This ensures we only check fields specified in the config, ignoring any extra fields
        details = {}
        missing = []
        
        for field_name in workflow_requirements:
            field_value = user_requirements.get(field_name)
            # Use field_name as field_type for special validation cases
            is_valid = self._validate_field(field_name, field_value, field_type=field_name)
            details[field_name] = is_valid
            if not is_valid:
                missing.append(field_name)
        
        # Calculate completeness score
        score = sum(details.values()) / len(workflow_requirements) if workflow_requirements else 0.0
        
        return {
            'score': score,
            'details': details,
            'missing': missing
        }
    
    def scanner_software_compatibility(
        self,
        compatibility_info: Dict[str, Union[str, int, float, List[str], Dict, None]]
    ) -> Dict[str, Union[float, Dict[str, bool]]]:
        """
        Compute a metric that evaluates if the AI tool ensures compatibility with
        reconstruction algorithms used on the imaging data during medical image acquisition.
        
        This metric checks for the presence of compatibility information regarding:
        - Scanner manufacturer
        - Scanner model
        - Reconstruction algorithms
        - Post-processing algorithms
        - Software version
        - Image format support
        - Acquisition parameters
        
        Parameters
        ----------
        compatibility_info : dict
            Dictionary containing scanner and software compatibility information.
            Expected keys:
            - 'scanner_manufacturer' (str): Scanner manufacturer name (e.g., 'Siemens', 'GE', 'Philips')
            - 'scanner_model' (str): Specific scanner model name
            - 'reconstruction_algorithms' (list): List of supported reconstruction algorithm names
            - 'post_processing_algorithms' (list): List of supported post-processing algorithm names
            - 'software_version' (str): Version of the reconstruction software
            - 'image_format' (str/list): Supported image format(s) (e.g., 'DICOM', 'NIfTI')
            - 'acquisition_parameters' (dict/list): Supported acquisition parameters or parameter ranges
            
        Returns
        -------
        dict
            Dictionary containing:
            - 'score' (float): Completeness score between 0.0 and 1.0
            - 'details' (dict): Boolean flags for each compatibility category
            - 'missing' (list): List of missing compatibility categories
            
        """
        # Use compatibility categories from instance variable (loaded from JSON)
        compatibility_categories = self.compatibility_categories
        
        # Check each category (only those defined in compatibility_categories)
        # This ensures we only check fields specified in the config, ignoring any extra fields
        details = {}
        missing = []
        
        for field_name in compatibility_categories:
            field_value = compatibility_info.get(field_name)
            
            # Special handling for image_format (can be str or list)
            if field_name == 'image_format':
                if isinstance(field_value, str):
                    is_valid = len(field_value.strip()) > 0
                elif isinstance(field_value, (list, tuple)):
                    is_valid = (
                        len(field_value) > 0 and
                        all(isinstance(fmt, str) and len(fmt.strip()) > 0 for fmt in field_value)
                    )
                else:
                    is_valid = False
            # Special handling for acquisition_parameters (can be dict or list)
            elif field_name == 'acquisition_parameters':
                if isinstance(field_value, dict):
                    is_valid = len(field_value) > 0
                elif isinstance(field_value, (list, tuple)):
                    is_valid = len(field_value) > 0
                else:
                    is_valid = False
            else:
                # Use generic validation for other fields
                is_valid = self._validate_field(field_name, field_value)
            
            details[field_name] = is_valid
            if not is_valid:
                missing.append(field_name)
        
        # Calculate completeness score
        score = sum(details.values()) / len(compatibility_categories) if compatibility_categories else 0.0
        
        return {
            'score': score,
            'details': details,
            'missing': missing
        }
    
    def operational_medical_sites_score(
        self,
        medical_site_info: Dict[str, Union[str, None]]
    ) -> Dict[str, Union[float, Dict[str, bool]]]:
        """
        Compute a metric that evaluates if information about the operational medical site
        which is going to run the AI tool is properly reported.
        
        This metric checks for the presence of:
        - Department
        - Section
        - Specialty
        - Clinical site type (e.g., hospital, clinical center, primary care)
        
        Parameters
        ----------
        medical_site_info : dict
            Dictionary containing operational medical site information. Expected keys:
            - 'department' (str): Department name
            - 'section' (str): Section name
            - 'specialty' (str): Medical specialty
            - 'clinical_site_type' (str): Clinical site type (e.g., 'hospital', 'clinical center', 'primary care')
            
        Returns
        -------
        dict
            Dictionary containing:
            - 'score' (float): Completeness score between 0.0 and 1.0
            - 'details' (dict): Boolean flags for each medical site category
            - 'missing' (list): List of missing medical site categories
            
        """
        # Use operational medical sites categories from instance variable (loaded from JSON)
        operational_medical_sites_categories = self.operational_medical_sites_categories
        
        # Check each category (only those defined in operational_medical_sites_categories)
        # This ensures we only check fields specified in the config, ignoring any extra fields
        details = {}
        missing = []
        
        for field_name in operational_medical_sites_categories:
            field_value = medical_site_info.get(field_name)
            # All fields in this metric are strings, use generic validation
            is_valid = self._validate_field(field_name, field_value)
            details[field_name] = is_valid
            if not is_valid:
                missing.append(field_name)
        
        # Calculate completeness score
        score = sum(details.values()) / len(operational_medical_sites_categories) if operational_medical_sites_categories else 0.0
        
        return {
            'score': score,
            'details': details,
            'missing': missing
        }

