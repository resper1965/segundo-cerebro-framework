from conftest import gerar


def test_gera_cerebro_minimo_com_arquivo_de_respostas(tmp_path):
    destino = gerar(tmp_path / "c")
    respostas = (destino / ".copier-answers.yml").read_text(encoding="utf-8")
    assert "nome: Cliente Teste" in respostas
    assert "modulos: []" in respostas
