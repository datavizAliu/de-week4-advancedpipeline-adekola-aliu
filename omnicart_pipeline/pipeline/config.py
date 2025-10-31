import configparser
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: str = "../pipeline.cfg"):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
    
    def get(self, section:str, key:str, fallback=None):
        """ 
        generic getter  with optional fallback
        """
        return self.config.get(section,key, fallback=fallback)
    
    def getint(self, section:str, key:str, fallback=None):
        """
        For integers values
        """
        return self.config.getint(section, key, fallback=fallback)
    def getfloat(self, section:str, key:str, fallback=None):
        """
        For float values
        """
        return self.config.getfloat(section, key, fallback=fallback)
    