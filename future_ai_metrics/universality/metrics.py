"""
Machine Learning Metrics for Measuring Universality of Predictive Models.

This module provides a comprehensive set of metrics to evaluate how well
a predictive model generalizes across different domains, datasets, and conditions.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict
import warnings
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
                self.real_requirements = config.get('real_requirements', [])
                self.compatibility_categories = config.get('compatibility_categories', [])
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}. "
                "Please ensure the config/universality_metrics_config.json file exists in the project root."
            )
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in configuration file {config_path}: {e}"
            )
        
        if not self.real_requirements:
            raise ValueError(
                "No required categories found in configuration file. "
                "The 'real_requirements' key must contain a non-empty list."
            )
        
        if not self.compatibility_categories:
            raise ValueError(
                "No compatibility categories found in configuration file. "
                "The 'compatibility_categories' key must contain a non-empty list."
            )
    
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
        
        Parameters
        ----------
        user_requirements : dict
            Dictionary containing infrastructure user_requirements. Expected keys:
            - 'hardware_type' (str): 'cpu' or 'gpu'
            - 'ram_memory' (int/float): RAM amount in GB
            - 'disk_space' (int/float): Hard disk space in GB
            - 'operating_system' (str): OS name/version
            - 'libraries' (list): List of required library names
            
        Returns
        -------
        dict
            Dictionary containing:
            - 'score' (float): Completeness score between 0.0 and 1.0
            - 'details' (dict): Boolean flags for each requirement category
            - 'missing' (list): List of missing requirement categories
            
        """
        # Use required categories from instance variable (loaded from JSON)
        real_requirements = self.real_requirements
        
        # Check each category (only those defined in real_requirements)
        details = {}
        missing = []
        
        # Check hardware_type
        if 'hardware_type' in real_requirements:
            hardware_type = user_requirements.get('hardware_type')
            details['hardware_type'] = (
                hardware_type is not None and 
                isinstance(hardware_type, str) and 
                hardware_type.lower() in ['cpu', 'gpu']
            )
            if not details['hardware_type']:
                missing.append('hardware_type')
        
        # Check RAM memory
        if 'ram_memory' in real_requirements:
            ram_memory = user_requirements.get('ram_memory')
            details['ram_memory'] = (
                ram_memory is not None and 
                isinstance(ram_memory, (int, float)) and 
                ram_memory > 0
            )
            if not details['ram_memory']:
                missing.append('ram_memory')
        
        # Check disk space
        if 'disk_space' in real_requirements:
            disk_space = user_requirements.get('disk_space')
            details['disk_space'] = (
                disk_space is not None and 
                isinstance(disk_space, (int, float)) and 
                disk_space > 0
            )
            if not details['disk_space']:
                missing.append('disk_space')
        
        # Check operating system
        if 'operating_system' in real_requirements:
            operating_system = user_requirements.get('operating_system')
            details['operating_system'] = (
                operating_system is not None and 
                isinstance(operating_system, str) and 
                len(operating_system.strip()) > 0
            )
            if not details['operating_system']:
                missing.append('operating_system')
        
        # Check libraries
        if 'libraries' in real_requirements:
            libraries = user_requirements.get('libraries')
            details['libraries'] = (
                libraries is not None and 
                isinstance(libraries, (list, tuple)) and 
                len(libraries) > 0 and
                all(isinstance(lib, str) and len(lib.strip()) > 0 for lib in libraries)
            )
            if not details['libraries']:
                missing.append('libraries')
        
        # Calculate completeness score
        score = sum(details.values()) / len(real_requirements)
        
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
        details = {}
        missing = []
        
        # Check scanner_manufacturer
        if 'scanner_manufacturer' in compatibility_categories:
            scanner_manufacturer = compatibility_info.get('scanner_manufacturer')
            details['scanner_manufacturer'] = (
                scanner_manufacturer is not None and 
                isinstance(scanner_manufacturer, str) and 
                len(scanner_manufacturer.strip()) > 0
            )
            if not details['scanner_manufacturer']:
                missing.append('scanner_manufacturer')
        
        # Check scanner_model
        if 'scanner_model' in compatibility_categories:
            scanner_model = compatibility_info.get('scanner_model')
            details['scanner_model'] = (
                scanner_model is not None and 
                isinstance(scanner_model, str) and 
                len(scanner_model.strip()) > 0
            )
            if not details['scanner_model']:
                missing.append('scanner_model')
        
        # Check reconstruction_algorithms
        if 'reconstruction_algorithms' in compatibility_categories:
            reconstruction_algorithms = compatibility_info.get('reconstruction_algorithms')
            details['reconstruction_algorithms'] = (
                reconstruction_algorithms is not None and 
                isinstance(reconstruction_algorithms, (list, tuple)) and 
                len(reconstruction_algorithms) > 0 and
                all(isinstance(alg, str) and len(alg.strip()) > 0 for alg in reconstruction_algorithms)
            )
            if not details['reconstruction_algorithms']:
                missing.append('reconstruction_algorithms')
        
        # Check software_version
        if 'software_version' in compatibility_categories:
            software_version = compatibility_info.get('software_version')
            details['software_version'] = (
                software_version is not None and 
                isinstance(software_version, str) and 
                len(software_version.strip()) > 0
            )
            if not details['software_version']:
                missing.append('software_version')
        
        # Check image_format
        if 'image_format' in compatibility_categories:
            image_format = compatibility_info.get('image_format')
            # Can be a string or a list of strings
            if isinstance(image_format, str):
                details['image_format'] = len(image_format.strip()) > 0
            elif isinstance(image_format, (list, tuple)):
                details['image_format'] = (
                    len(image_format) > 0 and
                    all(isinstance(fmt, str) and len(fmt.strip()) > 0 for fmt in image_format)
                )
            else:
                details['image_format'] = False
            if not details['image_format']:
                missing.append('image_format')
        
        # Check acquisition_parameters
        if 'acquisition_parameters' in compatibility_categories:
            acquisition_parameters = compatibility_info.get('acquisition_parameters')
            # Can be a dict or a list
            if isinstance(acquisition_parameters, dict):
                details['acquisition_parameters'] = len(acquisition_parameters) > 0
            elif isinstance(acquisition_parameters, (list, tuple)):
                details['acquisition_parameters'] = len(acquisition_parameters) > 0
            else:
                details['acquisition_parameters'] = False
            if not details['acquisition_parameters']:
                missing.append('acquisition_parameters')
        
        # Calculate completeness score
        score = sum(details.values()) / len(compatibility_categories)
        
        return {
            'score': score,
            'details': details,
            'missing': missing
        }

