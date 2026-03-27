# seed.py
import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd

def criar_banco():
    """Cria o banco de dados e popula com os dados"""
    
    conn = sqlite3.connect('ordens_servico.db')
    cursor = conn.cursor()
    
    # Criar tabela com nova coluna servidores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sei_numero TEXT UNIQUE NOT NULL,
            processo TEXT NOT NULL,
            comunidade TEXT NOT NULL,
            municipio TEXT,
            data_publicacao DATE NOT NULL,
            prazo_dias INTEGER NOT NULL,
            data_termino DATE,
            tipo_acao TEXT NOT NULL,
            situacao TEXT DEFAULT 'Vigente',
            observacao TEXT,
            servidores TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Limpar dados existentes
    cursor.execute("DELETE FROM ordens_servico")
    
    # Dados das ordens de serviço com servidores
    ordens = [
        # OS Vigentes com servidores
        (26965751, "54230.000810/2010-61", "Vila Fé em Deus", "Santa Rita", "2026-01-14", 120, "Elaboração de RTID", "Vigente", "", 
         "Francisco Elivan Arruda Rodrigues, Miguel Pereira dos Anjos Filho, Nilza Maria Santos Silva, Henrique Jorge Mota Chagas, Michael Jackson Miranda Cardoso"),
        (27006505, "54230.001872/2007-95", "Ilha do Cajual", "Alcântara", "2026-01-16", 120, "Elaboração de RTID", "Vigente", "", 
         "Marcos Henrique Barbosa Ferreira, Souhayl Ayoubi, Lucas Pinheiro Gariani"),
        (27075961, "54230.003668/2005-47", "Bom Sucesso", "Mata Roma", "2026-01-29", 180, "Elaboração de RTID", "Vigente", "", 
         "Marcos Henrique Barbosa Ferreira, Souhayl Ayoubi, Lidiane Carvalho Amorim de Sousa Dourado"),
        (27133903, "54230.001112/2016-79", "Cocalinho", "Parnarama", "2026-01-29", 120, "Elaboração de RTID", "Vigente", "", 
         "Lucas Pinheiro Gariani, Aldenir Moreira Costa, Claudionor Silva Pereira, Lidiane Carvalho Amorim de Sousa Dourado"),
        (27134821, "54230.000423/2007-20", "Oiteiro dos Nogueiras", "Itapecuru-Mirim", "2026-01-29", 90, "Elaboração de RTID", "Vigente", "", 
         "Francisco Elivan Arruda Rodrigues, Miguel Pereira dos Anjos Filho, Henrique Jorge Mota Chagas, Nilza Maria Santos Silva, Michael Jackson Miranda Cardoso"),
        (27138427, "54230.012664/2010-17", "Lago do Coco", "Matões do Norte", "2026-01-29", 90, "Elaboração de RTID", "Vigente", "", 
         "Lucas Pinheiro Gariani, Claudionor Silva Pereira, Aldenir Moreira Costa, Lidiane Carvalho Amorim de Sousa Dourado"),
        (27167058, "54230.000592/2014-99", "Imbiral/Cabeça Branca", "Pedro do Rosário", "2026-02-02", 120, "Elaboração de RTID", "Vigente", "", 
         "Claudionor Silva Pereira, Aldenir Moreira Costa, Francisco Elivan Arruda Rodrigues, Miguel Pereira dos Anjos Filho, Nilza Maria Santos Silva, Henrique Jorge Mota Chagas, Lidiane Carvalho Amorim de Sousa Dourado"),
        (27271515, "54230.000939/2017-46", "Malhadalta de Adão", "Nina Rodrigues", "2026-02-10", 140, "Elaboração de RTID", "Vigente", "", 
         "Francisco Elivan Arruda Rodrigues, Geandro Carvalho Castro, Nilza Maria Santos Silva, Henrique Jorge Mota Chagas, Michael Jackson Miranda Cardoso, Cosme Oliveira Moura Júnior"),
        (27308299, "54000.095289/2024-41", "Santa Luzia (Fazenda Piscicultura São José)", "Santa Rita", "2026-02-12", 30, "Vistoria e avaliação", "Vigente", "", 
         "Paulo Eduardo Ferreira Mendes, Geandro Carvalho Castro, Antônio de Fatima Pereira dos Santos"),
        (27318063, "54000.101260/2021-63", "Cedro", "Santa Rita", "2026-02-12", 160, "Elaboração de RTID", "Vigente", "", 
         "Cosme Oliveira Moura Junior, Rosangela Lima Brasil, Francisco Elivan Arruda Rodrigues, Miguel Pereira dos Anjos Filho, Aldenir Moreira Costa, Claudionor Silva Pereira, Bernadete Braga, Nilza Maria Santos Silva, Henrique Jorge Mota Chagas, Michael Jackson Miranda Cardoso"),
        (27354586, "54230.004781/2004-69", "Monte Alegre Olho Dágua dos Grilos", "São Luiz Gonzaga", "2026-02-24", 90, "Elaboração de RTID", "Vigente", "", 
         "Lucas Pinheiro Gariani, Souhayl Ayoubi, Lidiane Carvalho Amorim de Sousa Dourado"),
        (27355478, "54230.004000/2009-41", "Joaquim e Maria", "Miranda do Norte", "2026-02-20", 90, "Elaboração de RTID", "Vigente", "", 
         "Lucas Gariani Pinheiro Gariani, Verônica Kaezer da Silva, Umberto Cesaroli Junior, Aldenir Moreira Costa"),
        (27389014, "54230.000413/2007-94", "Sumaúma/Mata III", "Itapecuru-Mirim", "2026-02-24", 120, "Elaboração de RTID", "Vigente", "", 
         "Stefany Silva Dornelas, Aldenir Moreira Costa, Lucas Pinheiro Gariani, Umberto Cerasoli Junior, Veronica Kaezer da Silva"),
        (27390912, "54000.097056/2023-01", "Santo Antônio dos Coelhos", "Vargem Grande", "2026-02-24", 120, "Elaboração de RTID", "Vigente", "", 
         "Umberto Cerasoli Junior, Aldenir Moreira Costa, Lucas Pinheiro Gariani, Veronica Kaezer da Silva"),
        (27444224, "54230.007875/2011-19", "Canto do Lago", "Paulino Neves", "2026-02-27", 180, "Elaboração de RTID", "Vigente", "", 
         "Mauricio Sousa Matos, Geandro Carvalho Castro, Nilza Maria dos Santos, Henrique Jorge Mota Chaves, Aldenir Moreira Costa, Rodrigo Marinho Alexandre"),
        (27446886, "54000.036422/2022-66", "Vila Nova/Boi Baiano", "São Mateus", "2026-02-27", 180, "Elaboração de RTID", "Vigente", "", 
         "Veronica Kaezer da Silva, Geandro Carvalho Castro, Nilza Maria dos Santos, Henrique Jorge Mota Chaves, Lucas Pinheiro Gariani, Aldenir Moreira Costa"),
        (27466280, "54230.003938/2011-68", "Vera Cruz", "Serrano do Maranhão", "2026-03-02", 0, "Convalidação de atos", "Vigente", "", ""),
        
        # OS Vencidas (algumas com servidores)
        (26010277, "01089.000282/2017-31", "Projeto de Assentamento Entroncamento / Território Quilombola Santa Rosa dos Pretos", "Itapecuru-Mirim", "2025-10-22", 60, "Regularização ocupacional", "Vencida", "", 
         "Webert Cordeiro Cantanhede Sobrinho, Francisco Elivan Arruda Rodrigues, Nilza Maria Santos Silva, Miguel Pereira dos Anjos Filho, Carlos Saudanha Araújo de Carvalho"),
        (26076213, "54230.003794/2004-11", "Santa Rosa dos Pretos e Monge Belo", "Itapecuru Mirim/Anajatuba", "2025-11-04", 120, "Vistoria e avaliação", "Vencida", "", 
         "Celso Viana Botentuit, Miguel Pereira dos Anjos, Francisco Elivan Arruda Rodrigues, Joel Nunes Pereira, Martfran Albuquerque de Sousa"),
        (25752463, "54230.001495/2005-22", "Mocambo", "Itapecuru-Mirim", "2025-10-02", 120, "Elaboração de RTID", "Vencida", "", 
         "Rodrigo Marinho Alexandre, Silvânia Maria Corrêa de Oliveira, Henrique Jorge Mota Chagas, Aldenir Moreira Costa, Claudionor Silva Pereira"),
        (25768296, "54230.001872/2007-95", "Ilha do Cajual", "Alcântara", "2025-10-03", 120, "Elaboração de RTID", "Vencida", "", 
         "Marcos Henrique Barbosa Ferreira, Silvânia Maria Corrêa de Oliveira, Henrique Jorge Mota Chagas, Aldenir Moreira Costa, Claudionor Silva Pereira"),
        (25770349, "54230.000931/2006-27", "Vista Alegre", "Itapecuru-Mirim", "2025-10-03", 120, "Elaboração de RTID", "Vencida", "", 
         "Lucas Pinheiro Gariani, Silvânia Maria Corrêa de Oliveira, Henrique Jorge Mota Chagas, Aldenir Moreira Costa, Claudionor Silva Pereira"),
        (25772334, "54230.000577/2007-11", "Jaguarana/Floresta", "Colinas", "2025-10-03", 120, "Elaboração de RTID", "Vencida", "", 
         "Maria Paula Baesso Moura, Silvânia Maria Corrêa de Oliveira, Henrique Jorge Mota Chagas, Aldenir Moreira Costa, Claudionor Silva Pereira"),
        (25808371, "54230.009564/2010-11", "Depósito", "Brejo", "2025-10-07", 120, "Vistoria e avaliação", "Vencida", "", 
         "Celso Viana Botentuit, Silvânia Maria Corrêa de Oliveira, Henrique Jorge Mota Chagas"),
        (25874692, "54230.011263/2010-40", "Jutay", "Monção", "2025-10-10", 120, "Elaboração de RTID", "Vencida", "", 
         "Cosme Oliveira Moura Junior, Rosangela Lima Brasil, Silvânia Maria Corrêa de Oliveira, Henrique Jorge Mota Chagas, Aldenir Moreira Costa, Claudionor Silva Pereira, Bernadete Braga Santos"),
    ]
    
    hoje = date.today()
    
    # Inserir dados
    for ordem in ordens:
        sei_numero, processo, comunidade, municipio, data_pub, prazo, tipo, situacao, observacao, servidores = ordem
        
        data_pub_date = datetime.strptime(data_pub, '%Y-%m-%d').date()
        data_termino = data_pub_date + timedelta(days=prazo) if prazo > 0 else None
        
        # Atualizar situação se necessário
        if data_termino and data_termino < hoje and situacao == 'Vigente':
            situacao = 'Vencida'
        
        try:
            cursor.execute('''
                INSERT INTO ordens_servico 
                (sei_numero, processo, comunidade, municipio, data_publicacao, prazo_dias, 
                 data_termino, tipo_acao, situacao, observacao, servidores)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(sei_numero), str(processo), str(comunidade), str(municipio), 
                  data_pub, int(prazo), data_termino, str(tipo), str(situacao), str(observacao), str(servidores)))
        except Exception as e:
            print(f"Erro ao inserir ordem {sei_numero}: {e}")
    
    conn.commit()
    
    # Verificar dados inseridos
    cursor.execute("SELECT COUNT(*) FROM ordens_servico")
    count = cursor.fetchone()[0]
    print(f"✅ Banco de dados criado com sucesso!")
    print(f"📊 Total de ordens inseridas: {count}")
    
    # Mostrar resumo
    cursor.execute("SELECT situacao, COUNT(*) FROM ordens_servico GROUP BY situacao")
    resultados = cursor.fetchall()
    print("\n📊 Resumo por situação:")
    for situacao, total in resultados:
        print(f"   {situacao}: {total}")
    
    conn.close()

if __name__ == "__main__":
    criar_banco()