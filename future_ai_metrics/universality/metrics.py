"""
Machine Learning Metrics for Measuring Universality of Predictive Models.

This module provides a comprehensive set of metrics to evaluate how well
a predictive model generalizes across different domains, datasets, and conditions.
"""

from typing import Dict, List, Optional, Union
import json
import os

from .utils import (
    extract_field_names,
    extract_field_metadata,
    check_completeness,
    check_validity,
    compute_metrics
)


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
            Path to the JSON configuration file containing workflow requirements,
            scanner compatibility categories, operational medical sites, and operational countries.
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
                # Extract field names from the new structure (supports both old and new format)
                self.workflow_requirements = extract_field_names(config.get('workflow_requirements', []))
                self.workflow_requirements_metadata = extract_field_metadata(config.get('workflow_requirements', []))
                self.compatibility_categories = extract_field_names(config.get('compatibility_categories', []))
                self.compatibility_categories_metadata = extract_field_metadata(config.get('compatibility_categories', []))
                self.operational_medical_sites_categories = extract_field_names(config.get('operational_medical_sites_categories', []))
                self.operational_medical_sites_metadata = extract_field_metadata(config.get('operational_medical_sites_categories', []))
                self.operational_countries_categories = extract_field_names(config.get('operational_countries_categories', []))
                self.operational_countries_metadata = extract_field_metadata(config.get('operational_countries_categories', []))
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
        
        if not self.operational_countries_categories:
            raise ValueError(
                "No operational countries categories found in configuration file. "
                "The 'operational_countries_categories' key must contain a non-empty list."
            )
    
    def workflow_requirements_score(
        self,
        user_requirements: Dict[str, Union[str, int, float, List[str], None]]
    ) -> Dict[str, Union[float, Dict[str, bool]]]:
        """
        Compute metrics that evaluate if the digital infrastructure settings
        for executing the AI tool are properly reported.
        
        This metric checks for the presence and validity of:
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
            - 'completeness_score' (float): Score for field presence (0.0 to 1.0)
            - 'validity_score' (float): Score for field validity according to definitions (0.0 to 1.0)
            - 'completeness_details' (dict): Boolean flags for each field's presence
            - 'validity_details' (dict): Boolean flags for each field's validity
            - 'missing' (list): List of missing requirement categories
            - 'invalid' (list): List of invalid requirement categories
            
        """
        return compute_metrics(
            self.workflow_requirements,
            self.workflow_requirements_metadata,
            user_requirements
        )
    
    def scanner_software_compatibility(
        self,
        compatibility_info: Dict[str, Union[str, int, float, List[str], Dict, None]]
    ) -> Dict[str, Union[float, Dict[str, bool]]]:
        """
        Compute metrics that evaluate if the AI tool ensures compatibility with
        reconstruction algorithms used on the imaging data during medical image acquisition.
        
        This metric checks for the presence and validity of compatibility information regarding:
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
            - 'completeness_score' (float): Score for field presence (0.0 to 1.0)
            - 'validity_score' (float): Score for field validity according to definitions (0.0 to 1.0)
            - 'completeness_details' (dict): Boolean flags for each field's presence
            - 'validity_details' (dict): Boolean flags for each field's validity
            - 'missing' (list): List of missing compatibility categories
            - 'invalid' (list): List of invalid compatibility categories
            
        """
        return compute_metrics(
            self.compatibility_categories,
            self.compatibility_categories_metadata,
            compatibility_info
        )
    
    def operational_medical_sites_score(
        self,
        medical_site_info: Dict[str, Union[str, None]]
    ) -> Dict[str, Union[float, Dict[str, bool]]]:
        """
        Compute metrics that evaluate if information about the operational medical site
        which is going to run the AI tool is properly reported.
        
        This metric checks for the presence and validity of:
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
            - 'completeness_score' (float): Score for field presence (0.0 to 1.0)
            - 'validity_score' (float): Score for field validity according to definitions (0.0 to 1.0)
            - 'completeness_details' (dict): Boolean flags for each field's presence
            - 'validity_details' (dict): Boolean flags for each field's validity
            - 'missing' (list): List of missing medical site categories
            - 'invalid' (list): List of invalid medical site categories
            
        """
        return compute_metrics(
            self.operational_medical_sites_categories,
            self.operational_medical_sites_metadata,
            medical_site_info
        )
    
    def operational_countries_score(
        self,
        countries_info: Dict[str, Union[str, List[str], None]]
    ) -> Dict[str, Union[float, Dict[str, bool]]]:
        """
        Compute metrics that evaluate if information about the countries for which
        the AI tool is designed is properly reported, in terms of compliance with
        regulation aspects and legal implications.
        
        This metric checks for the presence and validity of:
        - Countries: List of countries where the tool is designed to operate
        - Regulations: List of applicable regulations and legal frameworks
        - Legal frameworks: List of compliance standards for each country
        
        Parameters
        ----------
        countries_info : dict
            Dictionary containing operational countries information. Expected keys:
            - 'countries' (list): List of country names or ISO codes (e.g., ['USA', 'EU', 'UK'])
            - 'regulations' (list): List of regulations that apply (e.g., ['GDPR', 'FDA', 'MDR', 'HIPAA'])
            - 'legal_frameworks' (list): List of legal frameworks and compliance standards
            
        Returns
        -------
        dict
            Dictionary containing:
            - 'completeness_score' (float): Score for field presence (0.0 to 1.0)
            - 'validity_score' (float): Score for field validity according to definitions (0.0 to 1.0)
            - 'completeness_details' (dict): Boolean flags for each field's presence
            - 'validity_details' (dict): Boolean flags for each field's validity
            - 'missing' (list): List of missing country-related categories
            - 'invalid' (list): List of invalid country-related categories
            
        """
        return compute_metrics(
            self.operational_countries_categories,
            self.operational_countries_metadata,
            countries_info
        )

