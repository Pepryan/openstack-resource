import pandas as pd
import datetime
import config

class Formatter:
    """Utility class for formatting data"""
    
    @staticmethod
    def format_ram(ram):
        """
        Format RAM size
        
        Args:
            ram (int): RAM size in MB
            
        Returns:
            str: Formatted RAM size
        """
        if ram >= 1024:
            return f"{ram // 1024}G"
        else:
            return f"{ram}M"
        
    @staticmethod
    def format_public(is_public):
        """
        Format public flag
        
        Args:
            is_public (bool): Public flag
            
        Returns:
            str: Formatted public flag
        """
        return 'Yes' if is_public else 'No'
        
    @staticmethod
    def format_swap(swap):
        """
        Format swap size
        
        Args:
            swap (int): Swap size in MB
            
        Returns:
            str: Formatted swap size
        """
        if swap >= 1024:
            swap = int(swap)
            return f"{swap // 1024}G"
        elif swap < 1024:
            swap = int(swap)
            return f"{swap}M"
        else:
            return '-'
        
    @staticmethod
    def format_properties(properties):
        """
        Format properties
        
        Args:
            properties (str): Properties
            
        Returns:
            str: Formatted properties
        """
        return '-' if pd.isna(properties) else properties

    @staticmethod
    def format_timestamp(timestamp):
        """
        Format timestamp
        
        Args:
            timestamp (float): Timestamp
            
        Returns:
            str: Formatted timestamp
        """
        return datetime.datetime.fromtimestamp(timestamp).strftime(config.DATE_FORMAT)
        
    @staticmethod
    def format_empty_value(value):
        """
        Format empty value
        
        Args:
            value: Value to format
            
        Returns:
            str: Formatted value
        """
        if pd.isna(value) or value == '':
            return '-'
        return value
