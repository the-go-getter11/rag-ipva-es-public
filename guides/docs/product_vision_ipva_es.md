# IPVA Insight ES — Visão de Produto

## Visão geral
"IPVA Insight ES" é uma plataforma SaaS de inteligência fiscal especializada no Imposto sobre a Propriedade de Veículos Automotores (IPVA) do Espírito Santo. O produto combina um motor RAG com fluxos de automação para entregar respostas confiáveis, monitoramento contínuo e orientação operacional para pessoas físicas, frotistas, contabilistas e dealers que lidam com obrigações do IPVA/ES.

## Problema dos clientes
- **Normas fragmentadas e dinâmicas**: legislação estadual, decretos e comunicados sofrem atualizações frequentes, tornando difícil acompanhar alíquotas, isenções e novos procedimentos.
- **Risco de autuações e perda de descontos**: atrasos ou interpretações equivocadas geram multas, inscrição em dívida ativa, apreensão de veículos e perda de descontos de cota única.
- **Processos manuais e dispersos**: cálculo, emissão de guias e controle de pagamentos exigem acessar vários portais, planilhas e e-mails.
- **Falta de orientação personalizada**: escritórios de contabilidade e gestores de frota precisam adaptar regras às características de cada cliente (veículos novos, blindados, empréstimo mercantil, isenção para PcD, locadoras etc.).

## Por que eles pagariam
- **Redução de riscos**: alertas antecipados e análises contextualizadas evitam multas, juros e apreensões, algo que pode custar múltiplas vezes o valor da assinatura.
- **Economia de tempo**: consultas instantâneas, checklists automatizados e relatórios consolidados reduzem horas de pesquisa manual por parte de contadores e gestores.
- **Confiança e rastreabilidade**: cada resposta traz referências às normas oficiais, garantindo segurança jurídica ao embasar pareceres ou relatórios.
- **Repasses fiscais otimizados**: frotistas e dealers conseguem planejar desembolsos e repasses com base nas regras vigentes, gerando ganho de fluxo de caixa.

## Segmentos prioritários
1. Escritórios contábeis e BPOs fiscais focados em empresas capixabas.
2. Locadoras e frotistas que operam veículos registrados no ES.
3. Concessionárias e revendas que precisam orientar clientes sobre transferência, 1º licenciamento e incidência do IPVA.
4. Pessoas físicas de alta renda que desejam consultoria premium para gestão tributária de veículos especiais.

## Principais capacidades
- **Assistente de compliance IPVA** alimentado por RAG com fontes oficiais do ES, citando dispositivos legais e vigências.
- **Monitor fiscal contínuo** com alerts sobre mudanças normativas, calendário de pagamento e exigências documentais.
- **Simulador e calculadora** que parametriza alíquotas, descontos, isenções e multas específicos do ES.
- **Workflow de regularização** que orienta passo a passo processos como parcelamento, contestação, baixa e transferência.
- **Dashboard multi-cliente** para escritórios e frotistas acompanharem obrigações, comprovantes e pendências.

## Diferenciais competitivos
- Foco hiperlocal no IPVA do Espírito Santo, mapeando peculiaridades regionais (ex.: veículos locados, isenções PcD, convênios interestaduais).
- Respostas auditáveis com citações numeradas e histórico de versões dos atos normativos.
- Integração-ready com DETRAN/ES, SEFAZ/ES e CRLV via APIs ou automações RPA para emissão/validação automática de guias.
- Camada de workflow que transforma a resposta do modelo em tarefas práticas com prazos, anexos e responsáveis.

## Estratégia de monetização
- **Plano Pro (R$ 249/mês)**: até 10 veículos, histórico de consultas, relatórios PDF e suporte por e-mail.
- **Plano Business (R$ 749/mês)**: até 200 veículos, alertas automáticos, integrações básicas (webhooks, ERP) e suporte prioritário.
- **Plano Enterprise (sob consulta)**: limites sob demanda, automações personalizadas, API dedicada e SLAs contratuais.
- Upsell de serviços premium: pareceres revisados por advogados parceiros, auditoria anual de IPVA e treinamentos in-company.

## Métricas norteadoras
- Taxa de renovações e churn por segmento.
- Tempo médio de resolução de dúvidas (consulta → resposta).
- Redução de penalidades registradas pelos clientes.
- Número de alterações legais processadas e publicadas na base em até 24h.

## Roadmap inicial
1. Conectar e versionar fontes normativas oficiais do ES (leis, decretos, RIPVA, comunicados SEFAZ, DETRAN).
2. Construir pipeline de ingestão, chunking e indexação com critérios alinhados a temas IPVA.
3. Implementar o assistente em Streamlit com login multi-tenant e histórico por cliente.
4. Adicionar calculadora/simulador alinhada ao ano vigente e regras de desconto.
5. Lançar monitor fiscal com alertas automáticos de calendário e mudanças legais.
