# Arquitetura RAG — IPVA Insight ES

## Fontes prioritárias
- **Legislação primária**: Lei nº 6.999/2001, RIPVA/ES, decretos, portarias e instruções normativas publicadas no DOE-ES.
- **Atos complementares**: Resoluções do DETRAN/ES, comunicados SEFAZ/ES, convênios CONFAZ relevantes.
- **Conteúdo operacional**: manuais de procedimentos, formulários oficiais, FAQs e comunicados sobre calendário, parcelamentos e descontos.

## Pipeline de ingestão e versionamento
1. **Coleta automatizada**
   - Agentes de scraping + RSS do DOE-ES para novas publicações.
   - Integração com APIs ou download semanal de conjuntos do CONFAZ e DETRAN.
2. **Normalização**
   - Conversão para Markdown estruturado (YAML front-matter: `uf`, `fonte`, `vigencia`, `assunto`).
   - Extração de metadados (datas de publicação, vigência, órgão emissor, tipo de documento).
3. **Rastreabilidade**
   - Armazenar o PDF/HTML original em storage versionado (S3/Azure Blob) com hash SHA256.
   - Manter changelog com diff semântico entre versões sucessivas.

## Processamento e chunking
- **Pre-processamento**: limpeza de cabeçalhos repetitivos, tabelas convertidas em formato CSV markdown, manter citações de artigos.
- **Segmentação**: chunks de 400-600 tokens, preservando artigos completos. Atributos extras por chunk: tema (alíquota, isenção, fiscalização), tipo de veículo, período de vigência.
- **Embeddings**
  - **Primário**: `text-embedding-004` (Gemini) para semântica profunda.
  - **Fallback**: TF-IDF local com expansão lexical (sinônimos, siglas) para consultas sem API key.
- **Armazenamento**: vetor store em `FAISS` (local) + metadados em `DuckDB` para filtros estruturados.

## Recuperação e orquestração
- **Retrieval híbrido**: combinação de similaridade vetorial + BM25 + filtros por vigência/órgão.
- **Re-ranking**: modelo cross-encoder leve (`bge-reranker-base`) para ordenar top-k.
- **Context Composer**: builder que agrupa chunks por documento, gera sumários bulletados e injeta notas de vigência.
- **Prompting**
  - System prompt enfatizando papel de consultor tributário ES e necessidade de citar `[n]` com data.
  - Prompt estrutural com slots: pergunta, contexto, checklist (vigência, valor, procedimento), formato de resposta (resumo + passo a passo + referências).
- **Geração**: modelo padrão `gemini-2.5-flash`; fallback `gpt-4o-mini` ou `llama-3.1-70b` hospedadp via API.
- **Guardrails**
  - Classificador upstream para detectar consultas fora de domínio (não-IPVA) e responder com mensagem de escopo.
  - Validação pós-gera ção: regra regex para garantir presença de pelo menos uma referência `[n]` e datas claras.

## Pós-processamento
- **Explicabilidade**: anexar seção "Base normativa" com link direto ao trecho original e hash.
- **Tarefas acionáveis**: gerar checklist estruturado (JSON) para alimentar módulo de workflow.
- **Armazenamento de histórico**: log das consultas com prompt, contexto, resposta, feedback do usuário e carimbo temporal.

## Observabilidade e qualidade
- **Avaliação automática**: conjunto de perguntas canônicas (cobrança, isenção PcD, veículos locados, atrasos) com respostas gabarito.
- **Feedback humano**: dashboards com thumbs-up/down, comentários, marcação de desatualização.
- **Metricas-chave**: precisão de citações, compliance com formato, latência < 3s (cache de contexto), taxa de fallback.

## Segurança e conformidade
- **Gestão de credenciais** via `.env` + Azure Key Vault / GCP Secret Manager.
- **LGPD**: anonimização de dados pessoais em logs, retenção máxima de 18 meses, opt-out por cliente.
- **Auditoria**: trilha de auditoria de quem acessou ou exportou relatórios.
