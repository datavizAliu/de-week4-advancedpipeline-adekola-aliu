import configparser
from pipeline.config import ConfigManager

def test_confi_manager_reads_values(tmp_path):
    config_content = """

    [api]
    base_url = https://example.com
    limit = 10
     """
    
    cfg_file = tmp_path / "test.cfg"
    cfg_file.write_text(config_content)

    config = ConfigManager(config_path=cfg_file)

    assert config.get("api", "base_url") == "https://example.com"
    assert config.getint("api", "limit") == 10