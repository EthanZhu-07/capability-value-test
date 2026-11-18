# Capability Value Test｜Validação do valor de uma nova capacidade

[English](README.md)｜[简体中文](README.zh-CN.md)｜[繁體中文](README.zh-TW.md)｜[日本語](README.ja.md)｜[한국어](README.ko.md)｜[Русский](README.ru.md)｜[हिन्दी](README.hi.md)｜[Español](README.es.md)｜[Français](README.fr.md)｜[Deutsch](README.de.md)｜**Português**｜[العربية](README.ar.md)

> Tornar visível o uso de uma nova capacidade e mensurável o valor que ela cria.

Capability Value Test é um Skill geral para agentes de IA. Ele verifica se uma capacidade recém-integrada (como Skill, modelo, plugin, MCP Server, navegador, componente de código aberto ou fluxo de agente) foi realmente usada e se cria valor mensurável em relação ao método anterior.

O Skill projeta um teste A/B justo entre o método anterior e o método habilitado pela nova capacidade. Uma pessoa revisa o desenho completo antes da execução. Ao final, é gerado um relatório HTML independente, visual e rastreável.

## Perguntas respondidas

1. **A capacidade foi realmente usada e onde está a evidência?**
2. **Ela criou valor e esse valor pode ser quantificado?**
3. **O processo de uso e o valor concreto podem ser compreendidos visualmente?**

## Processo

1. Definir a nova capacidade e os métodos antes e depois da integração.
2. Escolher uma tarefa real que ambos os métodos possam concluir.
3. Alinhar entradas, ambiente, restrições, escopo de medição e critérios de avaliação.
4. Apresentar o desenho completo para revisão humana e revisá-lo se for rejeitado.
5. Executar os dois métodos somente após aprovação explícita, registrando resultados, métricas e evidências.
6. Analisar as diferenças e gerar o relatório HTML.

O objetivo não é fazer a nova capacidade vencer, mas descobrir o que mudou e se as evidências justificam sua adoção.

## Relatório HTML

1. **Recomendação final**: adotar, não adotar ou evidência insuficiente; inclui cenários adequados e inadequados.
2. **Valor e benefícios**: qualidade, tempo total, Token, custo, etapas, erros e novas tentativas.
3. **Prova de uso**: a última seção guarda separadamente comandos, chamadas de ferramentas, entradas, saídas, logs, horários, IDs de tarefa e estados.

Métricas indisponíveis aparecem como “Não disponível”, nunca como zero. Segredos devem ser removidos.

## Instalação

```bash
npx -y skills add EthanZhu-07/capability-value-test -g --all
```

Ou clone o repositório e siga a convenção de diretório de Skills do seu agente:

```bash
git clone https://github.com/EthanZhu-07/capability-value-test.git
```

## Exemplo de uso

```text
Use Capability Value Test para comparar meu método atual de navegador com o método habilitado pelo Lightpanda. Mostre primeiro o desenho do teste.
```

## Gerar o relatório manualmente

```bash
python3 scripts/render_report.py tests/sample-experiment.json --output report.html
```

O gerador usa apenas a biblioteca padrão do Python e cria um único HTML que funciona offline.

A versão mais recente usa um formato de relatório fixo e versionado. Todos os relatórios mantêm as mesmas seções e a mesma ordem, com uma explicação abaixo de cada título principal. O idioma padrão acompanha o idioma da conversa do usuário e pode ser alterado no canto superior direito. A análise separa os resultados do experimento, a pesquisa externa com fontes e a recomendação final, descrevendo cada cenário por uma pessoa, uma tarefa e um ambiente concretos.

## Limites

- Uma execução por método fornece evidência direcional, não garantia estatística.
- Os dois métodos precisam concluir a mesma tarefa representativa.
- Token e custo só são comparados quando o host os fornece.
- Se o uso não puder ser verificado, o resultado deve ser “Evidência insuficiente”.
- A execução headless é apresentada como registro, não como gravação ao vivo.

## Licença

Atualmente não há arquivo de licença. O fato de o repositório ser público não concede, por si só, permissão para copiar, modificar ou redistribuir o projeto.
