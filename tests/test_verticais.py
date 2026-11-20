import yaml

from conftest import gerar


def _modulos_gerados(c):
    return yaml.safe_load((c / ".copier-answers.yml").read_text(encoding="utf-8"))["modulos"]


def test_vertical_juridico_ativa_modulos_e_dependencias(tmp_path):
    c = gerar(tmp_path / "j", vertical="juridico", modulos=None)
    for pasta in ["06-clientes", "11-casos", "12-teses", "13-modelos", "14-jurisprudencia"]:
        assert (c / pasta).is_dir(), pasta


def test_vertical_pessoal(tmp_path):
    c = gerar(tmp_path / "p", vertical="pessoal", modulos=None)
    assert (c / "15-objetivos").is_dir() and (c / "16-leituras").is_dir()
    assert not (c / "06-clientes").exists()


def test_teses_puxa_casos_e_modelos(tmp_path):
    c = gerar(tmp_path / "t", modulos=["teses"])
    assert (c / "11-casos").is_dir() and (c / "13-modelos").is_dir() and (c / "06-clientes").is_dir()
