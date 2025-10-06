# Plano de implementação — IPVA Insight ES

## 1. Preparação operacional
- **Governança**: definir squad (engenharia de dados, ML engineer, especialista tributário, designer) e rituais semanais.
- **Infraestrutura**: provisionar repositório Git privado, ambiente cloud (GCP ou Azure) e pipelines CI/CD.
- **Backlog inicial**: priorizar funcionalidades MVP (assistente RAG + monitor de calendário).

## 2. Ingestão e curadoria de dados
1. **Inventário de fontes**: mapear todos os atos legais do IPVA/ES, comunicados e FAQs oficiais.
2. **Captura automática**: implementar scrapers e integrações (DOE-ES, SEFAZ, DETRAN, CONFAZ).
3. **Padronização**: converter documentos para Markdown estruturado com metadados (vigência, assunto, tipo de veículo).
4. **Controle de versões**: armazenar originais em storage com versionamento e registrar diffs semânticos.
5. **Qualidade**: checklists de completude, datas e assinaturas; revisar semanalmente com especialista tributário.

## 3. Pipeline RAG
- **Indexação**
  - Expandir `project/rag/indexer.py` para suportar filtros por vigência, órgão e tipo de veículo.
  - Criar etapa de chunking avançado (artigos/tabelas) com tamanho alvo 400-600 tokens.
  - Persistir embeddings em FAISS + DuckDB com metadados estruturados.
- **Retrieval**
  - Implementar busca híbrida (vector + BM25) e re-ranking com cross-encoder.
  - Adicionar filtros no método `Engine.retrieve` para vigência e tema.
- **Geração**
  - Revisar prompt no `Engine.answer` para produzir seções padronizadas (Resumo, Passos, Referências).
  - Incluir validações pós-geraç ão (referências, datas, disclaimers) e fallback offline (TF-IDF + template).
- **Observabilidade**
  - Registrar logs detalhados de consultas, contexto recuperado, latência e feedback.
  - Configurar avaliação automática com conjunto de perguntas gabaritadas.

## 4. Aplicativo e UX
- **Autenticação e multi-tenant**: adicionar login (Auth0/Keycloak) e escopos por cliente.
- **Fluxo do usuário**
  - Tela principal com assistente de perguntas.
  - Painel de alertas (calendário IPVA, mudanças legais).
  - Módulo "Ações" com checklists gerados automaticamente.
- **Calculadora/Simulador**
  - Implementar módulo para cálculo de IPVA por veículo (base, alíquota, desconto, multa).
  - Exportar relatórios em PDF compilando consultas + simulações.
- **Feedback loop**
  - Botões de aprovação/reprovação e campo de comentários por resposta.
  - Dashboard interno com métricas de satisfação e temas recorrentes.

## 5. Monetização e produto
- **Planos e billing**: integrar serviço de cobrança (Stripe, Asaas) com limites por número de veículos/consultas.
- **Gestão de contratos**: permitir anexar documentação de SLA, controlar acesso de usuários corporativos.
- **Suporte premium**: canal direto para dúvidas complexas, com escalonamento a especialistas legais.

## 6. Segurança e conformidade
- Criptografia em repouso e trânsito, segregação de dados por cliente.
- Adequação LGPD: política de retenção, consentimento e anonimização de dados pessoais.
- Monitoramento de acesso e auditoria de exportações.

## 7. Cronograma sugerido (12 semanas)
- **Semanas 1-2**: setup, coleta inicial de dados, protótipo RAG básico.
- **Semanas 3-5**: pipeline de ingestão automatizado, indexação avançada, MVP Streamlit.
- **Semanas 6-8**: funcionalidades premium (monitor fiscal, simulador, workflow).
- **Semanas 9-10**: integrações externas, billing e segurança.
- **Semanas 11-12**: testes com clientes piloto, ajustes finais e lançamento beta.

## 8. Próximos passos imediatos
1. Revisar lista de fontes e assinar convênios quando necessário.
2. Rodar `indexer.py` com base inicial de documentos reais.
3. Configurar `.env` com chaves do Gemini e parâmetros do ambiente.
4. Montar script de avaliação automática para monitorar qualidade das respostas iniciais.
